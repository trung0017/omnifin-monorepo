import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { ShieldAlert, Activity, CreditCard, RefreshCw } from 'lucide-react';

// Định nghĩa cấu trúc dữ liệu giao dịch giả lập luồng Kafka
interface TransactionMetric {
  time: string;
  tps: number;
  fraudCount: number;
}

interface FraudAlert {
  id: string;
  account: string;
  amount: number;
  reason: string;
  timestamp: string;
}

export default function App() {
  const [metrics, setMetrics] = useState<TransactionMetric[]>([]);
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);

  useEffect(() => {
    // Giả lập luồng nhận dữ liệu Real-time liên tục từ Spark Streaming Broker
    const interval = setInterval(() => {
      const now = new Date();
      const timeStr = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;

      // 1. Cập nhật biểu đồ thông lượng giao dịch (TPS)
      setMetrics((prev) => {
        const updated = [...prev, {
          time: timeStr,
          tps: Math.floor(Math.random() * 300) + 700, // Giả lập dao động xung quanh mốc 1000 TPS
          fraudCount: Math.floor(Math.random() * 3)
        }];
        if (updated.length > 8) updated.shift(); // Giữ tối đa 8 điểm biểu đồ để tối ưu bộ nhớ
        return updated;
      });

      // 2. Giả lập bẫy sự kiện phát hiện gian lận đột xuất
      if (Math.random() > 0.6) {
        const newAlert: FraudAlert = {
          id: Math.random().toString(36).substring(7).toUpperCase(),
          account: `102${Math.floor(Math.random() * 900000 + 100000)}`,
          amount: Math.floor(Math.random() * 50) * 1000000 + 15000000, // Các giao dịch giá trị lớn vượt hạn mức QĐ 2345
          reason: Math.random() > 0.5 ? "Phát hiện Liveness giả mạo (Anti-spoofing)" : "Tần suất giao dịch bất thường (High-frequency)",
          timestamp: "Aug 19, 2026, 9:44 AM"
        };
        setAlerts((prev) => [newAlert, ...prev].slice(0, 5)); // Lưu tối đa 5 cảnh báo mới nhất
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={styles.dashboardContainer}>
      {/* Thanh Tiêu Đề Hệ Thống */}
      <header style={styles.header}>
        <div style={styles.headerTitleArea}>
          <ShieldAlert color="#ff453a" size={28} style={{ marginRight: 10 }} />
          <h1 style={styles.mainTitle}>OmniFin Enterprise - Fraud Detection Dashboard</h1>
        </div>
        <div style={styles.badge}>Live Monitoring</div>
      </header>

      {/* Phân vùng các thẻ Chỉ số nhanh (KPI Cards) */}
      <section style={styles.kpiGrid}>
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <Activity color="#30d158" size={20} />
            <span style={styles.cardTitle}>Thông lượng Luồng chính</span>
          </div>
          <p style={styles.cardValue}>~1,000 TPS</p>
          <span style={styles.cardSubtitle}>Đang đọc từ Kafka Topic</span>
        </div>

        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <CreditCard color="#0a84ff" size={20} />
            <span style={styles.cardTitle}>Cảnh báo hệ thống</span>
          </div>
          <p style={styles.cardValue} style={{ color: '#ff453a' }}>{alerts.length} Sự cố</p>
          <span style={styles.cardSubtitle}>Phân tích thời gian thực qua Spark</span>
        </div>
      </section>

      {/* Khối Đồ thị & Nhật ký sự kiện */}
      <div style={styles.contentGrid}>
        {/* Đồ thị luồng TPS */}
        <div style={styles.chartWrapper}>
          <h3 style={styles.sectionTitle}>Tốc độ xử lý luồng giao dịch tài chính (Real-time TPS)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2c2c2e" />
              <XAxis dataKey="time" stroke="#aeaeade" />
              <YAxis stroke="#aeaeade" />
              <Tooltip contentStyle={{ backgroundColor: '#1c1c1e', borderColor: '#2c2c2e' }} />
              <Legend />
              <Line type="monotone" dataKey="tps" name="Thông lượng (Transactions/sec)" stroke="#0a84ff" strokeWidth={3} activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Bảng danh sách Cảnh báo Gian lận */}
        <div style={styles.alertWrapper}>
          <h3 style={styles.sectionTitle}>Nhật ký Sự kiện Nghi vấn (Fraud Log)</h3>
          <div style={styles.alertList}>
            {alerts.length === 0 ? (
              <p style={styles.emptyText}>Đang chờ luồng sự kiện truyền tải từ Big Data Layer... <RefreshCw size={14} style={styles.spin} /></p>
            ) : (
              alerts.map((alert) => (
                <div key={alert.id} style={styles.alertCard}>
                  <div style={styles.alertMeta}>
                    <span style={styles.alertId}>#{alert.id}</span>
                    <span style={styles.alertTime}>{alert.timestamp}</span>
                  </div>
                  <p style={styles.alertContent}>
                    Tài khoản: <strong>{alert.account}</strong> | Số tiền chuyển: <strong style={{ color: '#ff453a' }}>{alert.amount.toLocaleString()} VND</strong>
                  </p>
                  <p style={styles.alertReason}>Lý do chặn: {alert.reason}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  dashboardContainer: { minHeight: '100vh', backgroundColor: '#000000', color: '#ffffff', padding: '24px', fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1c1c1e', paddingBottom: '16px', marginBottom: '24px' },
  headerTitleArea: { display: 'flex', alignItems: 'center' },
  mainTitle: { fontSize: '22px', fontWeight: 'bold', margin: 0, color: '#ffffff' },
  badge: { backgroundColor: '#30d15822', color: '#30d158', border: '1px solid #30d158', padding: '4px 12px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' },
  kpiGrid: { display: 'flex', gap: '16px', marginBottom: '24px' },
  card: { flex: 1, backgroundColor: '#1c1c1e', border: '1px solid #2c2c2e', padding: '16px', borderRadius: '12px' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' },
  cardTitle: { fontSize: '14px', color: '#aeaeb2', fontWeight: '500' },
  cardValue: { fontSize: '28px', fontWeight: 'bold', margin: '0 0 4px 0' },
  cardSubtitle: { fontSize: '12px', color: '#636366' },
  contentGrid: { display: 'flex', flexDirection: 'column' as const, gap: '24px' },
  chartWrapper: { backgroundColor: '#1c1c1e', border: '1px solid #2c2c2e', padding: '20px', borderRadius: '12px' },
  sectionTitle: { fontSize: '16px', fontWeight: '600', margin: '0 0 16px 0', color: '#ffffff' },
  alertWrapper: { backgroundColor: '#1c1c1e', border: '1px solid #2c2c2e', padding: '20px', borderRadius: '12px' },
  alertList: { display: 'flex', flexDirection: 'column' as const, gap: '12px' },
  emptyText: { color: '#8e8e93', fontSize: '14px', textAlign: 'center' as const, padding: '20px' },
  alertCard: { backgroundColor: '#2c2c2e55', borderLeft: '4px solid #ff453a', padding: '12px', borderRadius: '6px' },
  alertMeta: { display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '12px' },
  alertId: { color: '#ff453a', fontWeight: 'bold' },
  alertTime: { color: '#8e8e93' },
  alertContent: { margin: '0 0 4px 0', fontSize: '14px' },
  alertReason: { margin: 0, fontSize: '13px', color: '#ff9f0a' },
  spin: { display: 'inline-block', marginLeft: '5px' }
};