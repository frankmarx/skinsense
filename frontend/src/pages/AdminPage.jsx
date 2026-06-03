import React from 'react';

export const AdminPanel = ({ eventList, triggerEvent, logs }) => (
  <section>
    <h2>Admin Panel</h2>
    <div style={{ margin: '20px 0' }}>
      <h3>Available Events</h3>
      {eventList.map(event => (
        <button key={event.action} onClick={() => triggerEvent(event.action)} style={{ marginRight: '10px' }}>
          {event.name}
        </button>
      ))}
    </div>
    <h3>Logs</h3>
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr><th>Action</th><th>Status</th><th>Time</th></tr>
      </thead>
      <tbody>
        {logs.map(log => (
          <tr key={log.id}>
            <td>{log.event_name}</td>
            <td>{log.status}</td>
            <td>{new Date(log.job_start_time).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </section>
);
