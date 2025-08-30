export interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  role: 'admin' | 'employee' | 'customer';
  avatar?: string;
}

export interface Farmer {
  id: string;
  beneficiaryId: string;
  beneficiaryName: string;
  phoneNo: string;
  aadharNo: string;
  scheme: 'MTS' | 'SADBHAV' | 'SAYLIP' | 'CROMPTON';
  selectionDate: string;
  circleName: string;
  talukaName: string;
  villageName: string;
  installer: string;
  ldDays: number;
  jsrStatus: 'Approved' | 'Pending' | 'Rejected';
  dispatchStatus: 'Not Dispatched' | 'In Transit' | 'Delivered';
  dispatchDate?: string;
  vehicleNo?: string;
  driverInfo?: string;
  installationStatus: 'Not Started' | 'In Progress' | 'Completed' | 'Issues';
  installationRemark?: string;
  icrStatus: 'Not Started' | 'In Progress' | 'Completed';
  createdAt: string;
  updatedAt: string;
  pumphp?: string; // Pump horsepower
  pumpHead?: string; // Pump head
}

export interface ChatMessage {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  content: string;
  tags: string[];
  mentions: string[];
  taskId?: string;
  timestamp: string;
  farmerId?: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string;
  assignedBy: string;
  status: 'pending' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  tags: string[];
  farmerId?: string;
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface DashboardStats {
  totalFarmers: number;
  pendingInstallations: number;
  completedInstallations: number;
  dispatchedToday: number;
  pendingTasks: number;
}