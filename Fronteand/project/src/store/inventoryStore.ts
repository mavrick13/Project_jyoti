import { create } from 'zustand';

export interface InventoryItem {
  id: number;
  category: 'motor' | 'controller' | 'solar_panel' | 'bos' | 'structure' | 'wire' | 'pipe';
  type: string;
  specification?: string;
  quantity: number;
  min_stock_level: number;
  unit_price?: number;
  supplier?: string;
  part_number?: string;
  description?: string;
  location?: string;
  document_url?: string;
  status: 'active' | 'inactive' | 'out_of_stock';
  is_low_stock: boolean;
  created_at: string;
  updated_at: string;
}

export interface InventoryTransaction {
  id: number;
  inventory_id: number;
  transaction_type: 'in' | 'out' | 'adjustment';
  quantity: number;
  previous_quantity: number;
  new_quantity: number;
  reference_type?: string;
  reference_id?: string;
  notes?: string;
  unit_cost?: number;
  created_at: string;
  created_by_user_id: number;
}

export interface FarmerDispatch {
  id: number;
  farmer_beneficiary_id: string;
  dispatch_date: string;
  status: string;
  total_value?: number;
  notes?: string;
  items: FarmerDispatchItem[];
}

export interface FarmerDispatchItem {
  id: number;
  inventory_id: number;
  quantity: number;
  unit_cost?: number;
  total_cost?: number;
  inventory: InventoryItem;
}

export interface InventoryStats {
  total_items: number;
  total_value: number;
  low_stock_items: number;
  out_of_stock_items: number;
  categories: Record<string, { items: number; total_quantity: number }>;
  recent_transactions: InventoryTransaction[];
}

export interface InventoryFilter {
  category?: string;
  type?: string;
  specification?: string;
  status?: string;
  low_stock_only?: boolean;
  search?: string;
}

interface InventoryState {
  items: InventoryItem[];
  loading: boolean;
  error: string | null;
  stats: InventoryStats | null;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  total: number;
  
  // Actions
  fetchInventory: (page?: number, filters?: InventoryFilter) => Promise<void>;
  createInventoryItem: (item: Omit<InventoryItem, 'id' | 'created_at' | 'updated_at' | 'is_low_stock'>) => Promise<void>;
  updateInventoryItem: (id: number, updates: Partial<InventoryItem>) => Promise<void>;
  deleteInventoryItem: (id: number) => Promise<void>;
  bulkUploadInventory: (items: Omit<InventoryItem, 'id' | 'created_at' | 'updated_at' | 'is_low_stock'>[]) => Promise<void>;
  uploadInventoryFile: (file: File) => Promise<void>;
  dispatchToFarmer: (farmerId: string, items: { inventory_id: number; quantity: number; unit_cost?: number }[], notes?: string) => Promise<void>;
  fetchStats: () => Promise<void>;
  clearError: () => void;
}

const API_BASE = '/api/inventory';

export const useInventoryStore = create<InventoryState>((set, get) => ({
  items: [],
  loading: false,
  error: null,
  stats: null,
  currentPage: 1,
  totalPages: 1,
  pageSize: 50,
  total: 0,

  fetchInventory: async (page = 1, filters = {}) => {
    set({ loading: true, error: null });
    
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: get().pageSize.toString(),
        ...Object.fromEntries(
          Object.entries(filters).filter(([, value]) => value !== undefined && value !== '')
        )
      });
      
      const response = await fetch(`${API_BASE}?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to fetch inventory');
      
      const data = await response.json();
      
      set({
        items: data.items,
        currentPage: data.page,
        totalPages: data.total_pages,
        total: data.total,
        loading: false
      });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  createInventoryItem: async (item) => {
    set({ loading: true, error: null });
    
    try {
      const response = await fetch(API_BASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(item),
      });
      
      if (!response.ok) throw new Error('Failed to create inventory item');
      
      // Refresh the inventory list
      await get().fetchInventory(get().currentPage);
      set({ loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  updateInventoryItem: async (id, updates) => {
    set({ loading: true, error: null });
    
    try {
      const response = await fetch(`${API_BASE}/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(updates),
      });
      
      if (!response.ok) throw new Error('Failed to update inventory item');
      
      // Refresh the inventory list
      await get().fetchInventory(get().currentPage);
      set({ loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  deleteInventoryItem: async (id) => {
    set({ loading: true, error: null });
    
    try {
      const response = await fetch(`${API_BASE}/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to delete inventory item');
      
      // Refresh the inventory list
      await get().fetchInventory(get().currentPage);
      set({ loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  bulkUploadInventory: async (items) => {
    set({ loading: true, error: null });
    
    try {
      const response = await fetch(`${API_BASE}/bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(items),
      });
      
      if (!response.ok) throw new Error('Failed to bulk upload inventory');
      
      // Refresh the inventory list
      await get().fetchInventory(get().currentPage);
      set({ loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  uploadInventoryFile: async (file) => {
    set({ loading: true, error: null });
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });
      
      if (!response.ok) throw new Error('Failed to upload inventory file');
      
      const result = await response.json();
      console.log('Upload result:', result);
      
      // Refresh the inventory list
      await get().fetchInventory(get().currentPage);
      set({ loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  dispatchToFarmer: async (farmerId, items, notes) => {
    set({ loading: true, error: null });
    
    try {
      const response = await fetch(`${API_BASE}/dispatch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          farmer_beneficiary_id: farmerId,
          items,
          notes,
        }),
      });
      
      if (!response.ok) throw new Error('Failed to dispatch inventory');
      
      // Refresh the inventory list
      await get().fetchInventory(get().currentPage);
      set({ loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  fetchStats: async () => {
    try {
      const response = await fetch(`${API_BASE}/stats/dashboard`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) throw new Error('Failed to fetch inventory stats');
      
      const stats = await response.json();
      set({ stats });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },

  clearError: () => set({ error: null }),
}));