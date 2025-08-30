import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date));
}

export function calculateLDDays(selectionDate: string): number {
  const today = new Date();
  const selection = new Date(selectionDate);
  const diffTime = Math.abs(today.getTime() - selection.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    'Approved': 'text-green-600 bg-green-50',
    'Pending': 'text-yellow-600 bg-yellow-50',
    'Rejected': 'text-red-600 bg-red-50',
    'Not Started': 'text-gray-600 bg-gray-50',
    'In Progress': 'text-blue-600 bg-blue-50',
    'Completed': 'text-green-600 bg-green-50',
    'Issues': 'text-red-600 bg-red-50',
    'Not Dispatched': 'text-gray-600 bg-gray-50',
    'In Transit': 'text-blue-600 bg-blue-50',
    'Delivered': 'text-green-600 bg-green-50',
  };
  return statusColors[status] || 'text-gray-600 bg-gray-50';
}