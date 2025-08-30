import {
  Calendar,
  Download,
  Edit3,
  MapPin,
  Plus,
  Search,
  Trash2
} from 'lucide-react';
import { useState } from 'react';
import { cn, getStatusColor } from '../lib/utils';
import { useStore } from '../store/useStore';
import { FarmerForm } from './FarmerForm';

export function FarmerManagement() {
  const { farmers, deleteFarmer } = useStore();
  const [showForm, setShowForm] = useState(false);
  const [editingFarmer, setEditingFarmer] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterScheme, setFilterScheme] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredFarmers = farmers.filter((farmer) => {
    const matchesSearch = 
      farmer.beneficiaryName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      farmer.beneficiaryId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      farmer.phoneNo.includes(searchTerm);
    
    const matchesScheme = filterScheme === 'all' || farmer.scheme === filterScheme;
    const matchesStatus = filterStatus === 'all' || farmer.installationStatus === filterStatus;
    
    return matchesSearch && matchesScheme && matchesStatus;
  });

  const handleEdit = (farmerId: string) => {
    setEditingFarmer(farmerId);
    setShowForm(true);
  };

  const handleDelete = (farmerId: string) => {
    if (confirm('Are you sure you want to delete this farmer record?')) {
      deleteFarmer(farmerId);
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingFarmer(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Farmer Management</h2>
          <p className="text-gray-600">Manage farmer data and installation status</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add Farmer</span>
        </button>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search by name, ID, or phone..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <select
              value={filterScheme}
              onChange={(e) => setFilterScheme(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Schemes</option>
              <option value="MTS">MTS</option>
              <option value="SADBHAV">SADBHAV</option>
              <option value="SAYLIP">SAYLIP</option>
              <option value="CROMPTON">CROMPTON</option>
            </select>
            
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="Not Started">Not Started</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
              <option value="Issues">Issues</option>
            </select>
            
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2">
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* Farmers Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Farmer Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scheme & Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Installation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PUMP DETAILS
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredFarmers.map((farmer) => (
                <tr key={farmer.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {farmer.beneficiaryName}
                      </div>
                      <div className="text-xs text-gray-500">
                        ID: {farmer.beneficiaryId}
                      </div>
                      <div className="text-xs text-gray-500">
                        📞 {farmer.phoneNo}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {farmer.scheme}
                      </div>
                      <div className="text-xs text-gray-500 flex items-center">
                        <MapPin className="w-3 h-3 mr-1" />
                        {farmer.villageName}, {farmer.talukaName}
                      </div>
                      <div className="text-xs text-gray-500">
                        {farmer.circleName}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      <span className={cn("inline-flex px-2 py-1 text-xs rounded-full", getStatusColor(farmer.jsrStatus))}>
                        JSR: {farmer.jsrStatus}
                      </span>
                      <br />
                      <span className={cn("inline-flex px-2 py-1 text-xs rounded-full", getStatusColor(farmer.dispatchStatus))}>
                        Dispatch: {farmer.dispatchStatus}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <span className={cn("inline-flex px-2 py-1 text-xs rounded-full", getStatusColor(farmer.installationStatus))}>
                        {farmer.installationStatus}
                      </span>
                      <div className="text-xs text-gray-500 mt-1">
                        Installer: {farmer.installer}
                      </div>
                      <div className="text-xs text-gray-500 flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        LD: {farmer.ldDays} days
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap ">
                    <div>
                      {farmer.pumphp && (
                        <div className="text-sm text-gray-900">
                          HP: {farmer.pumphp}
                        </div>
                      )}
                      {farmer.pumpHead && (
                        <div className="text-xs text-gray-500">
                          Head: {farmer.pumpHead}
                        </div>
                      )}
                      {!farmer.pumphp && !farmer.pumpHead && (
                        <div className="text-xs text-gray-400">
                          Not specified
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(farmer.id)}
                        className="text-blue-600 hover:text-blue-900 p-1 hover:bg-blue-50 rounded transition-colors"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(farmer.id)}
                        className="text-red-600 hover:text-red-900 p-1 hover:bg-red-50 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredFarmers.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-2">No farmers found</div>
            <div className="text-sm text-gray-500">
              {searchTerm || filterScheme !== 'all' || filterStatus !== 'all' 
                ? 'Try adjusting your search criteria' 
                : 'Start by adding your first farmer'}
            </div>
          </div>
        )}
      </div>

      {/* Farmer Form Modal */}
      {showForm && (
        <FarmerForm
          farmerId={editingFarmer}
          onClose={handleFormClose}
        />
      )}
    </div>
  );
}