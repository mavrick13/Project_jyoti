import { create } from 'zustand';
import { User, Farmer, ChatMessage, Task, DashboardStats } from '../types';
import { farmersData } from '../data/farmers';
import { messagesData } from '../data/messages';
import { tasksData } from '../data/tasks';

interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  
  // Farmers
  farmers: Farmer[];
  addFarmer: (farmer: Omit<Farmer, 'id' | 'createdAt' | 'updatedAt' | 'ldDays'>) => void;
  updateFarmer: (id: string, updates: Partial<Farmer>) => void;
  deleteFarmer: (id: string) => void;
  
  // Chat
  messages: ChatMessage[];
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  
  // Tasks
  tasks: Task[];
  addTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  
  // Dashboard
  dashboardStats: DashboardStats;
  updateDashboardStats: () => void;
}

export const useStore = create<AppState>((set, get) => ({
  // Auth
  user: null,
  isAuthenticated: false,
  login: async (email: string, password: string) => {
    // Mock authentication
    if (email === 'admin@jyoti.com' && password === 'admin123') {
      const user: User = {
        id: 'admin1',
        name: 'Admin User',
        email: 'admin@jyoti.com',
        phone: '9876543200',
        role: 'admin',
      };
      set({ user, isAuthenticated: true });
      return true;
    }
    if (email === 'employee@jyoti.com' && password === 'emp123') {
      const user: User = {
        id: 'employee1',
        name: 'Employee User',
        email: 'employee@jyoti.com',
        phone: '9876543201',
        role: 'employee',
      };
      set({ user, isAuthenticated: true });
      return true;
    }
    return false;
  },
  logout: () => set({ user: null, isAuthenticated: false }),
  
  // Farmers
  farmers: farmersData,
  addFarmer: (farmerData) => {
    const farmer: Farmer = {
      ...farmerData,
      id: Date.now().toString(),
      ldDays: calculateLDDays(farmerData.selectionDate),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    set((state) => ({ farmers: [...state.farmers, farmer] }));
    get().updateDashboardStats();
  },
  updateFarmer: (id, updates) => {
    set((state) => ({
      farmers: state.farmers.map((farmer) =>
        farmer.id === id
          ? { ...farmer, ...updates, updatedAt: new Date().toISOString() }
          : farmer
      ),
    }));
    get().updateDashboardStats();
  },
  deleteFarmer: (id) => {
    set((state) => ({
      farmers: state.farmers.filter((farmer) => farmer.id !== id),
    }));
    get().updateDashboardStats();
  },
  
  // Chat
  messages: messagesData,
  addMessage: (messageData) => {
    const message: ChatMessage = {
      ...messageData,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    };
    set((state) => ({ messages: [...state.messages, message] }));
  },
  
  // Tasks
  tasks: tasksData,
  addTask: (taskData) => {
    const task: Task = {
      ...taskData,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    set((state) => ({ tasks: [...state.tasks, task] }));
  },
  updateTask: (id, updates) => {
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.id === id
          ? { ...task, ...updates, updatedAt: new Date().toISOString() }
          : task
      ),
    }));
  },
  
  // Dashboard
  dashboardStats: {
    totalFarmers: 0,
    pendingInstallations: 0,
    completedInstallations: 0,
    dispatchedToday: 0,
    pendingTasks: 0,
  },
  updateDashboardStats: () => {
    const { farmers, tasks } = get();
    const today = new Date().toDateString();
    
    const stats: DashboardStats = {
      totalFarmers: farmers.length,
      pendingInstallations: farmers.filter(f => f.installationStatus !== 'Completed').length,
      completedInstallations: farmers.filter(f => f.installationStatus === 'Completed').length,
      dispatchedToday: farmers.filter(f => f.dispatchDate && new Date(f.dispatchDate).toDateString() === today).length,
      pendingTasks: tasks.filter(t => t.status !== 'completed').length,
    };
    
    set({ dashboardStats: stats });
  },
}));

function calculateLDDays(selectionDate: string): number {
  const today = new Date();
  const selection = new Date(selectionDate);
  const diffTime = Math.abs(today.getTime() - selection.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}