import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatDateTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function getStatusBadgeClass(status) {
  const statusClasses = {
    'Pending': 'badge-pending',
    'In Progress': 'badge-in-progress',
    'Processing': 'badge-processing',
    'Ready': 'badge-ready',
    'Completed': 'badge-completed',
    'Rejected': 'badge-rejected',
  };
  return statusClasses[status] || 'badge-pending';
}

export function getStatusColor(status) {
  const colors = {
    'Pending': '#eab308',
    'In Progress': '#3b82f6',
    'Processing': '#8b5cf6',
    'Ready': '#06b6d4',
    'Completed': '#22c55e',
    'Rejected': '#ef4444',
  };
  return colors[status] || '#6b7280';
}
