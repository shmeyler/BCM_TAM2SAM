import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminPanel = ({ user, onClose }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviting, setInviting] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/users`,
        { withCredentials: true }
      );
      setUsers(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const updateUserStatus = async (userId, updates) => {
    try {
      await axios.patch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}`,
        updates,
        { withCredentials: true }
      );
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update user');
    }
  };

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}`,
        { withCredentials: true }
      );
      fetchUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  const inviteUser = async (e) => {
    e.preventDefault();
    
    if (!inviteEmail.endsWith('@beebyclarkmeyler.com')) {
      alert('Only @beebyclarkmeyler.com email addresses can be invited');
      return;
    }

    setInviting(true);
    try {
      await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/invite-user`,
        {
          email: inviteEmail,
          name: inviteName || inviteEmail.split('@')[0]
        },
        { withCredentials: true }
      );
      
      setInviteEmail('');
      setInviteName('');
      setShowInviteForm(false);
      fetchUsers();
      alert('User invited successfully! They can now log in with their Google account.');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to invite user');
    } finally {
      setInviting(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-5xl my-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-6 rounded-t-xl">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-white">Admin Panel</h2>
              <p className="text-orange-100 text-sm mt-1">Manage user access and permissions</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-orange-600 rounded-lg p-2 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          <div className="mb-4 flex justify-between items-center">
            <p className="text-sm text-gray-600">
              Total Users: <span className="font-semibold">{users.length}</span>
            </p>
            <button
              onClick={fetchUsers}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium transition-colors"
            >
              🔄 Refresh
            </button>
          </div>

          {/* Users Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b-2 border-gray-200">
                  <th className="text-left p-4 font-semibold text-gray-700">User</th>
                  <th className="text-left p-4 font-semibold text-gray-700">Status</th>
                  <th className="text-left p-4 font-semibold text-gray-700">Role</th>
                  <th className="text-left p-4 font-semibold text-gray-700">Last Login</th>
                  <th className="text-right p-4 font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-4">
                      <div className="flex items-center space-x-3">
                        {u.picture ? (
                          <img src={u.picture} alt={u.name} className="w-10 h-10 rounded-full" />
                        ) : (
                          <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                            <span className="text-orange-600 font-semibold">{u.name.charAt(0)}</span>
                          </div>
                        )}
                        <div>
                          <div className="font-medium text-gray-900">{u.name}</div>
                          <div className="text-sm text-gray-500">{u.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                          u.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {u.is_active ? '✓ Active' : '✗ Inactive'}
                      </span>
                    </td>
                    <td className="p-4">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                          u.is_admin
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {u.is_admin ? '👑 Admin' : '👤 User'}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-gray-600">
                      {u.last_login ? new Date(u.last_login).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="p-4">
                      <div className="flex justify-end space-x-2">
                        {u.id !== user.id && (
                          <>
                            <button
                              onClick={() => updateUserStatus(u.id, { is_active: !u.is_active })}
                              className={`px-3 py-1 rounded text-xs font-medium ${
                                u.is_active
                                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                                  : 'bg-green-100 text-green-700 hover:bg-green-200'
                              }`}
                              title={u.is_active ? 'Deactivate' : 'Activate'}
                            >
                              {u.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                            <button
                              onClick={() => updateUserStatus(u.id, { is_admin: !u.is_admin })}
                              className={`px-3 py-1 rounded text-xs font-medium ${
                                u.is_admin
                                  ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                  : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                              }`}
                              title={u.is_admin ? 'Remove Admin' : 'Make Admin'}
                            >
                              {u.is_admin ? 'Remove Admin' : 'Make Admin'}
                            </button>
                            <button
                              onClick={() => deleteUser(u.id)}
                              className="px-3 py-1 bg-red-500 text-white rounded text-xs font-medium hover:bg-red-600"
                              title="Delete User"
                            >
                              Delete
                            </button>
                          </>
                        )}
                        {u.id === user.id && (
                          <span className="text-xs text-gray-400 italic">You</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {users.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <p>No users found</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 p-4 rounded-b-xl border-t border-gray-200">
          <p className="text-xs text-gray-600 text-center">
            💡 Tip: The first user to login automatically becomes an admin. You cannot deactivate or delete your own account.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;