'use client';
import React from 'react';

interface SwitchProps {
  checked: boolean;
  onChange: () => void;
}

export const Switch: React.FC<SwitchProps> = ({ checked, onChange }) => (
  <button
    type="button"
    onClick={onChange}
    className={`w-12 h-6 rounded-full relative cursor-pointer transition-colors duration-200 ${
      checked ? 'bg-gray-900' : 'bg-gray-200'
    }`}
    aria-checked={checked}
    role="switch"
  >
    <span
      className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all duration-200 shadow-sm ${
        checked ? 'left-[1.55rem]' : 'left-0.5'
      }`}
    />
    <span className="sr-only">{checked ? 'On' : 'Off'}</span>
  </button>
);

interface InputFieldProps {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  type?: 'text' | 'number';
}

export const InputField: React.FC<InputFieldProps> = ({
  label,
  value,
  onChange,
  type = 'text'
}) => (
  <div className="mb-4">
    <label className="block text-[15px] font-medium text-black mb-1.5">
      {label}
    </label>
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[15px] bg-white text-black focus:outline-none focus:border-gray-300"
    />
  </div>
);

interface SettingsCardProps {
  children: React.ReactNode;
  className?: string;
}

export const SettingsCard: React.FC<SettingsCardProps> = ({ children, className = '' }) => (
  <div className={`bg-white text-black rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
    {children}
  </div>
);

interface SettingsSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: Array<{
    value: string;
    label: string;
  }>;
}

export const SettingsSelect: React.FC<SettingsSelectProps> = ({
  value,
  onChange,
  options,
}) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value)}
    className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-black outline-none focus:ring-2 focus:ring-blue-500"
  >
    {options.map((option) => (
      <option key={option.value} value={option.value}>
        {option.label}
      </option>
    ))}
  </select>
);
