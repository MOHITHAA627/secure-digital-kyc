import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function AdminDashboard() {
  const [data, setData] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const isAdmin = localStorage.getItem('is_admin') === 'true';
    if (!token || !isAdmin) {
      navigate('/login');
      return;
    }
    const fetchAll = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:8000/admin/all-kyc', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setData(res.data);
      } catch (err) {
        navigate('/login');
      }
    };
    fetchAll();
  }, [navigate]);

  const statusColor = {
    APPROVED: '#10B981',
    REVIEW: '#F59E0B',
    REJECTED: '#EF4444'
  };

  const filteredRecords = data
    ? data.records.filter(r => statusFilter === 'ALL' || r.status === statusFilter)
    : [];

  return (
    <div style={styles.container}>
      <div style={styles.wrapper}>
        <div style={styles.header}>
          <h1 style={styles.title}>🛡️ SecureKYC-AI — Admin</h1>
          <button
            style={styles.logoutBtn}
            onClick={() => {
              localStorage.removeItem('token');
              localStorage.removeItem('is_admin');
              navigate('/login');
            }}
          >
            Logout
          </button>
        </div>

        <p style={styles.welcome}>Global KYC overview across all users.</p>

        {data && (
          <>
            <div style={styles.statsRow}>
              <div style={styles.statCard}>
                <p style={styles.statNumber}>{data.total}</p>
                <p style={styles.statLabel}>Total KYC</p>
              </div>
              <div style={{ ...styles.statCard, borderColor: '#10B981' }}>
                <p style={{ ...styles.statNumber, color: '#10B981' }}>{data.approved}</p>
                <p style={styles.statLabel}>Approved</p>
              </div>
              <div style={{ ...styles.statCard, borderColor: '#F59E0B' }}>
                <p style={{ ...styles.statNumber, color: '#F59E0B' }}>{data.review}</p>
                <p style={styles.statLabel}>Under Review</p>
              </div>
              <div style={{ ...styles.statCard, borderColor: '#EF4444' }}>
                <p style={{ ...styles.statNumber, color: '#EF4444' }}>{data.rejected}</p>
                <p style={styles.statLabel}>Rejected</p>
              </div>
            </div>

            <div style={styles.filterRow}>
              <span style={styles.filterLabel}>Filter by status:</span>
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                style={styles.select}
              >
                <option value="ALL">All</option>
                <option value="APPROVED">Approved</option>
                <option value="REVIEW">Under Review</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>

            <div style={styles.tableWrapper}>
              <h2 style={styles.tableTitle}>📋 All KYC Records</h2>
              {filteredRecords.length === 0 ? (
                <p style={styles.noRecords}>No records for this filter.</p>
              ) : (
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Email</th>
                      <th style={styles.th}>Name</th>
                      <th style={styles.th}>District</th>
                      <th style={styles.th}>Age</th>
                      <th style={styles.th}>Risk Score</th>
                      <th style={styles.th}>Status</th>
                      <th style={styles.th}>Attempt</th>
                      <th style={styles.th}>Submitted</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRecords.map((r, i) => (
                      <tr key={i} style={styles.tr}>
                        <td style={styles.td}>{r.email}</td>
                        <td style={styles.td}>{r.name}</td>
                        <td style={styles.td}>{r.district}</td>
                        <td style={styles.td}>{r.age}</td>
                        <td style={styles.td}>{r.risk_score}</td>
                        <td style={styles.td}>
                          <span
                            style={{
                              ...styles.badge,
                              background: statusColor[r.status]
                            }}
                          >
                            {r.status}
                          </span>
                        </td>
                        <td style={styles.td}>{r.attempt_number}</td>
                        <td style={styles.td}>
                          {r.submission_date
                            ? new Date(r.submission_date).toLocaleString()
                            : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', background: '#080C14', padding: '20px' },
  wrapper: { maxWidth: '1100px', margin: '0 auto' },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
    paddingTop: '20px'
  },
  title: { color: '#00E5FF', fontSize: '22px' },
  logoutBtn: {
    background: 'transparent',
    color: '#EF4444',
    border: '1px solid #EF4444',
    padding: '8px 16px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '13px'
  },
  welcome: { color: '#888', marginBottom: '24px', fontSize: '14px' },
  statsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    marginBottom: '24px'
  },
  statCard: {
    background: '#0D1421',
    border: '1px solid #1A2540',
    borderRadius: '12px',
    padding: '20px',
    textAlign: 'center'
  },
  statNumber: {
    color: '#00E5FF',
    fontSize: '32px',
    fontWeight: 'bold',
    margin: '0 0 4px 0'
  },
  statLabel: { color: '#888', fontSize: '12px', margin: 0 },
  filterRow: {
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'center',
    marginBottom: '12px',
    gap: '8px'
  },
  filterLabel: { color: '#888', fontSize: '12px' },
  select: {
    background: '#131B2E',
    color: 'white',
    border: '1px solid #1A2540',
    borderRadius: '6px',
    padding: '6px 10px',
    fontSize: '12px'
  },
  tableWrapper: {
    background: '#0D1421',
    border: '1px solid #1A2540',
    borderRadius: '12px',
    padding: '24px'
  },
  tableTitle: { color: '#00E5FF', fontSize: '16px', marginBottom: '16px' },
  noRecords: { color: '#888', textAlign: 'center', padding: '20px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    color: '#888',
    fontSize: '12px',
    textAlign: 'left',
    padding: '10px',
    borderBottom: '1px solid #1A2540',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  },
  tr: { borderBottom: '1px solid #0D1421' },
  td: { color: 'white', fontSize: '13px', padding: '8px 10px' },
  badge: {
    padding: '4px 10px',
    borderRadius: '20px',
    fontSize: '11px',
    fontWeight: 'bold',
    color: '#000'
  }
};

export default AdminDashboard;

