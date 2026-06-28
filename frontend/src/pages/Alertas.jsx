import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { StatCard } from '../components/ui/StatCard';
import { Tabs } from '../components/ui/Tabs';
import { EmptyState } from '../components/ui/EmptyState';
import { SkeletonCard, SkeletonRow } from '../components/ui/Skeleton';
import {
  AlertTriangle, DollarSign, Clock, Users,
  ChevronDown, ChevronUp, ShieldAlert
} from 'lucide-react';

const formatCurrency = (val) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

const AlertCard = ({ icon, color, title, badge, children, borderColor }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card
      style={{
        borderLeft: `3px solid ${borderColor}`,
        animation: 'fadeInUp 0.3s ease-out both',
      }}
    >
      <div
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
          <div style={{
            width: 32, height: 32, borderRadius: 'var(--radius-sm)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: `${borderColor}15`, color: borderColor,
          }}>
            {icon}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{title}</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Badge color={color}>{badge}</Badge>
          {expanded ? <ChevronUp size={16} style={{ color: 'var(--text-tertiary)' }} /> : <ChevronDown size={16} style={{ color: 'var(--text-tertiary)' }} />}
        </div>
      </div>

      {expanded && (
        <div style={{
          marginTop: '0.875rem',
          paddingTop: '0.875rem',
          borderTop: '1px solid var(--panel-border)',
          animation: 'fadeInUp 0.2s ease-out',
        }}>
          {children}
        </div>
      )}
    </Card>
  );
};

export const Alertas = () => {
  const [anomaliasValor, setAnomaliasValor] = useState([]);
  const [anomaliasPrazo, setAnomaliasPrazo] = useState([]);
  const [anomaliasFornecedor, setAnomaliasFornecedor] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('valor');

  useEffect(() => {
    const fetchAlertas = async () => {
      try {
        const [valor, prazo, forn] = await Promise.all([
          api.get('/anomalias/valor-acima-media'),
          api.get('/anomalias/prazo-atipico'),
          api.get('/anomalias/fornecedor-recorrente'),
        ]);
        setAnomaliasValor(valor.data);
        setAnomaliasPrazo(prazo.data);
        setAnomaliasFornecedor(forn.data);
      } catch (err) {
        console.error('Erro ao carregar alertas:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAlertas();
  }, []);

  const tabs = [
    { key: 'valor', label: 'Valor Atípico', icon: <DollarSign size={14} />, count: anomaliasValor.length },
    { key: 'prazo', label: 'Prazo Atípico', icon: <Clock size={14} />, count: anomaliasPrazo.length },
    { key: 'fornecedor', label: 'Fornecedor Recorrente', icon: <Users size={14} />, count: anomaliasFornecedor.length },
  ];

  const totalAnomalias = anomaliasValor.length + anomaliasPrazo.length + anomaliasFornecedor.length;

  return (
    <div>
      <div className="page-header">
        <h1>Alertas e Anomalias</h1>
        <p>Anomalias detectadas automaticamente pelo sistema de regras.</p>
      </div>

      <div style={{ marginTop: '4rem', animation: 'fadeInUp 0.3s ease-out' }}>
        <EmptyState 
          icon={AlertTriangle} 
          title="Em Breve" 
          description="Essa funcionalidade está em desenvolvimento e estará disponível em breve." 
        />
      </div>
    </div>
  );
};
