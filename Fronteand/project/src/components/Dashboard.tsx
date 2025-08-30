import React, { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { 
  Users, 
  Calendar, 
  CheckCircle, 
  Truck, 
  AlertTriangle,
  TrendingUp,
  Clock,
  MapPin
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export function Dashboard() {
  const { dashboardStats, updateDashboardStats, farmers } = useStore();

  useEffect(() => {
    updateDashboardStats();
  }, [updateDashboardStats]);

  const schemeData = farmers.reduce((acc, farmer) => {
    acc[farmer.scheme] = (acc[farmer.scheme] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.entries(schemeData).map(([name, value]) => ({
    name,
    value,
  }));

  const statusData = [
    { name: 'Completed', value: farmers.filter(f => f.installationStatus === 'Completed').length },
    { name: 'In Progress', value: farmers.filter(f => f.installationStatus === 'In Progress').length },
    { name: 'Not Started', value: farmers.filter(f => f.installationStatus === 'Not Started').length },
    { name: 'Issues', value: farmers.filter(f => f.installationStatus === 'Issues').length },
  ];

  const recentActivity = farmers
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Farmers</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardStats.totalFarmers}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-green-600">20 farmers registered</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Installations</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardStats.pendingInstallations}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <AlertTriangle className="w-4 h-4 text-yellow-500 mr-1" />
            <span className="text-yellow-600">{dashboardStats.pendingInstallations} pending</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed Installations</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardStats.completedInstallations}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-green-600">{dashboardStats.completedInstallations} completed</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Dispatched Today</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardStats.dispatchedToday}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Truck className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <Calendar className="w-4 h-4 text-purple-500 mr-1" />
            <span className="text-purple-600">{dashboardStats.dispatchedToday} today</span>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Installation Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Scheme Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {recentActivity.map((farmer) => (
            <div key={farmer.id} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">
                  {farmer.beneficiaryName} ({farmer.beneficiaryId})
                </p>
                <p className="text-xs text-gray-500">
                  <MapPin className="w-3 h-3 inline mr-1" />
                  {farmer.villageName}, {farmer.talukaName}
                </p>
              </div>
              <div className="text-right">
                <p className={`text-xs px-2 py-1 rounded-full ${getStatusColor(farmer.installationStatus)}`}>
                  {farmer.installationStatus}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(farmer.updatedAt).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    'Completed': 'text-green-600 bg-green-50',
    'In Progress': 'text-blue-600 bg-blue-50',
    'Not Started': 'text-gray-600 bg-gray-50',
    'Issues': 'text-red-600 bg-red-50',
  };
  return statusColors[status] || 'text-gray-600 bg-gray-50';
}