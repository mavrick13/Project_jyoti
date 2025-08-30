import { X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';

interface FarmerFormProps {
  farmerId?: string | null;
  onClose: () => void;
}

export function FarmerForm({ farmerId, onClose }: FarmerFormProps) {
  const { farmers, addFarmer, updateFarmer } = useStore();
  const [formData, setFormData] = useState({
    beneficiaryId: '',
    beneficiaryName: '',
    phoneNo: '',
    aadharNo: '',
    scheme: 'MTS' as 'MTS' | 'SADBHAV' | 'SAYLIP' | 'CROMPTON',
    selectionDate: '',
    circleName: '',
    talukaName: '',
    villageName: '',
    installer: '',
    jsrStatus: 'Pending' as 'Pending' | 'Approved' | 'Rejected',
    dispatchStatus: 'Not Dispatched' as 'Not Dispatched' | 'In Transit' | 'Delivered',
    dispatchDate: '',
    vehicleNo: '',
    driverInfo: '',
    installationStatus: 'Not Started' as 'Not Started' | 'In Progress' | 'Completed' | 'Issues',
    installationRemark: '',
    icrStatus: 'Not Started' as 'Not Started' | 'In Progress' | 'Completed',
    pumphp:'0 HP' as '3-30 HP' | '3-50 HP' | '3-70 HP' | '5-30 HP' | '5-50 HP'| '5-70 HP' | '5-100 HP' |'7.5-30 HP' | '7.5-50 HP' | '7.5-70 HP' | '7.5-100 HP' ,
  });

  useEffect(() => {
    if (farmerId) {
      const farmer = farmers.find(f => f.id === farmerId);
      if (farmer) {
        setFormData({
          beneficiaryId: farmer.beneficiaryId,
          beneficiaryName: farmer.beneficiaryName,
          phoneNo: farmer.phoneNo,
          aadharNo: farmer.aadharNo,
          scheme: farmer.scheme,
          selectionDate: farmer.selectionDate,
          circleName: farmer.circleName,
          talukaName: farmer.talukaName,
          villageName: farmer.villageName,
          installer: farmer.installer,
          jsrStatus: farmer.jsrStatus,
          dispatchStatus: farmer.dispatchStatus,
          dispatchDate: farmer.dispatchDate || '',
          vehicleNo: farmer.vehicleNo || '',
          driverInfo: farmer.driverInfo || '',
          installationStatus: farmer.installationStatus,
          installationRemark: farmer.installationRemark || '',
          icrStatus: farmer.icrStatus,
          pumphp: ([
            '3-30 HP', '3-50 HP', '3-70 HP', '5-30 HP', '5-50 HP', '5-70 HP', '5-100 HP',
            '7.5-30 HP', '7.5-50 HP', '7.5-70 HP', '7.5-100 HP'
          ].includes(farmer.pumphp ?? '') ? (farmer.pumphp as string) : '3-30 HP') as
            '3-30 HP' | '3-50 HP' | '3-70 HP' | '5-30 HP' | '5-50 HP' | '5-70 HP' | '5-100 HP' |
            '7.5-30 HP' | '7.5-50 HP' | '7.5-70 HP' | '7.5-100 HP',
        });
      }
    }
  }, [farmerId, farmers]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (farmerId) {
      updateFarmer(farmerId, formData);
    } else {
      addFarmer(formData);
    }
    
    onClose();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {farmerId ? 'Edit Farmer' : 'Add New Farmer'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Beneficiary ID *
                </label>
                <input
                  type="text"
                  name="beneficiaryId"
                  value={formData.beneficiaryId}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Beneficiary Name *
                </label>
                <input
                  type="text"
                  name="beneficiaryName"
                  value={formData.beneficiaryName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  name="phoneNo"
                  value={formData.phoneNo}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Aadhar Number *
                </label>
                <input
                  type="text"
                  name="aadharNo"
                  value={formData.aadharNo}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Scheme and Location */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Scheme & Location</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Scheme *
                </label>
                <select
                  name="scheme"
                  value={formData.scheme}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="MTS">MTS</option>
                  <option value="SADBHAV">SADBHAV</option>
                  <option value="SAYLIP">SAYLIP</option>
                  <option value="CROMPTON">CROMPTON</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Selection Date *
                </label>
                <input
                  type="date"
                  name="selectionDate"
                  value={formData.selectionDate}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Circle Name *
                </label>
                <input
                  type="text"
                  name="circleName"
                  value={formData.circleName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Taluka Name *
                </label>
                <input
                  type="text"
                  name="talukaName"
                  value={formData.talukaName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Village Name *
                </label>
                <input
                  type="text"
                  name="villageName"
                  value={formData.villageName}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Installer *
                </label>
                <input
                  type="text"
                  name="installer"
                  value={formData.installer}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>
          </div>

          {/* Status Information */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Status Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  JSR Status
                </label>
                <select
                  name="jsrStatus"
                  value={formData.jsrStatus}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="Pending">Pending</option>
                  <option value="Approved">Approved</option>
                  <option value="Rejected">Rejected</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dispatch Status
                </label>
                <select
                  name="dispatchStatus"
                  value={formData.dispatchStatus}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="Not Dispatched">Not Dispatched</option>
                  <option value="In Transit">In Transit</option>
                  <option value="Delivered">Delivered</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Installation Status
                </label>
                <select
                  name="installationStatus"
                  value={formData.installationStatus}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="Not Started">Not Started</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                  <option value="Issues">Issues</option>
                </select>
              </div>
            </div>
          </div>

          {/* Dispatch Information */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Dispatch Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dispatch Date
                </label>
                <input
                  type="date"
                  name="dispatchDate"
                  value={formData.dispatchDate}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Vehicle Number
                </label>
                <input
                  type="text"
                  name="vehicleNo"
                  value={formData.vehicleNo}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Driver Information
                </label>
                <input
                  type="text"
                  name="driverInfo"
                  value={formData.driverInfo}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Installation Details */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Installation Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ICR Status
                </label>
                <select
                  name="icrStatus"
                  value={formData.icrStatus}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="Not Started">Not Started</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pump HP
                  </label>
                <input  
                    type="text"
                    name="pumphp"
                    value={formData.pumphp}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder='Enter Pump HP'
                />
                </div>
                
              <div className="md:col-span-2 lg:col-span-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">


                          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Upload Document
            </label>
            <input
              type="file"
              name="document"
              onChange={e => {
                if (e.target.files && e.target.files[0]) {
                  // You can set this to state or handle as needed
                  const files = e.target.files;
                  if (files && files[0]) {
                    setFormData(prev => ({ ...prev, document: files[0] }));
                  }
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>







                  Installation Remarks
                </label>
                <textarea
                  name="installationRemark"
                  value={formData.installationRemark}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Any issues or notes about the installation"
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {farmerId ? 'Update Farmer' : 'Add Farmer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}