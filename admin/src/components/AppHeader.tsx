import type { ReactNode } from 'react';
import logo from '../assets/logo.svg';

export default function AppHeader({ title, left, right }: { title: string; left?: ReactNode; right?: ReactNode }) {
  return (
    <header className="app-header">
      {left}
      {!left && <img src={logo} alt="Martínez Gas-Plomería" />}
      <h1>{title}</h1>
      {right}
    </header>
  );
}
