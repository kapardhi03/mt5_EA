
"use client";
import React, { createContext, useContext, useEffect, useState } from 'react';


type Theme = 'light' | 'dark';

interface ThemeContextType {
	theme: Theme | undefined;
	toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
		const [theme, setTheme] = useState<Theme | undefined>(undefined);

	// Only set theme after mount to avoid hydration mismatch
	useEffect(() => {
		let initialTheme: Theme = 'light';
		if (typeof window !== 'undefined') {
			initialTheme = (localStorage.getItem('theme') as Theme) ||
				(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
		}
		setTheme(initialTheme);
	}, []);

	useEffect(() => {
		if (theme) {
			document.documentElement.setAttribute('data-theme', theme);
			localStorage.setItem('theme', theme);
		}
	}, [theme]);

		const toggleTheme = () => {
			setTheme((prev: Theme | undefined) => (prev === 'light' ? 'dark' : 'light'));
		};

	// Don't render children until theme is set on client
	if (!theme) return null;

	return (
		<ThemeContext.Provider value={{ theme, toggleTheme }}>
			{children}
		</ThemeContext.Provider>
	);
};

export function useTheme() {
	const context = useContext(ThemeContext);
	if (!context) throw new Error('useTheme must be used within a ThemeProvider');
	return context;
}
