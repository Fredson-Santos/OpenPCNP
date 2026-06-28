import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { StatCard } from '../components/ui/StatCard';
import { Card } from '../components/ui/Card';
import { SkeletonCard } from '../components/ui/Skeleton';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import {
  FileText, DollarSign, Building2, MapPin
} from 'lucide-react';

const formatCurrency = (val) => {
  if (val >= 1e9) return `R$ ${(val / 1e9).toFixed(1)}B`;
  if (val >= 1e6) return `R$ ${(val / 1e6).toFixed(1)}M`;
  if (val >= 1e3) return `R$ ${(val / 1e3).toFixed(0)}K`;
  return `R$ ${val}`;
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--panel-bg-solid)',
      border: '1px solid var(--panel-border)',
      borderRadius: 'var(--radius-md)',
      padding: '0.625rem 0.875rem',
      fontSize: '0.8125rem',
    }}>
      <div style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
        {label ? label.split('-').reverse().join('/') : ''}
      </div>
      <div style={{ fontWeight: 600 }}>{payload[0].value.toLocaleString('pt-BR')} licitações</div>
    </div>
  );
};

export const Home = () => {
  const [stats, setStats] = useState(null);
  const [evolucao, setEvolucao] = useState([]);
  const [rankEstados, setRankEstados] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, evoRes, estRes] = await Promise.all([
          api.get('/stats'),
          api.get('/stats/evolucao-diaria'),
          api.get('/ranking/estados?limit=5&t=1'),
        ]);
        setStats(statsRes.data);
        setEvolucao(evoRes.data);
        setRankEstados(estRes.data);
      } catch (err) {
        console.error('Erro ao carregar dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const maxEstado = rankEstados.length > 0
    ? Math.max(...rankEstados.map((e) => e.total_licitacoes))
    : 1;

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1>Painel Geral</h1>
          <p>Visão macro das licitações públicas no Brasil.</p>
        </div>
        {stats?.ultima_atualizacao && (
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Última atualização: {new Date(stats.ultima_atualizacao).toLocaleDateString('pt-BR')}
          </div>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-3" style={{ marginBottom: '1.5rem' }}>
          <SkeletonCard /><SkeletonCard /><SkeletonCard />
        </div>
      ) : (
        <div className="grid grid-cols-3" style={{ marginBottom: '1.5rem' }}>
          <StatCard
            icon={<FileText size={20} />}
            label="Licitações"
            value={stats?.total_licitacoes?.toLocaleString('pt-BR') ?? '—'}
            detail="total cadastradas"
            accentColor="blue"
          />
          <StatCard
            icon={<DollarSign size={20} />}
            label="Valor Total"
            value={stats ? formatCurrency(stats.valor_total) : '—'}
            detail="em licitações"
            accentColor="green"
          />
          <StatCard
            icon={<Building2 size={20} />}
            label="Órgãos Ativos"
            value={stats?.orgaos_ativos?.toLocaleString('pt-BR') ?? '—'}
            detail="publicando editais"
            accentColor="purple"
          />
        </div>
      )}

      <div className="grid grid-cols-2" style={{ marginBottom: '1.5rem' }}>
        <Card variant="elevated">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600 }}>Evolução Diária</h3>
            <span className="text-xs text-secondary">Licitações publicadas por dia</span>
          </div>
          <div style={{ width: '100%', height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={evolucao.slice(-30)} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorQtd" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent-blue)" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="var(--accent-blue)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                <XAxis
                  dataKey="data"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: 'var(--text-tertiary)', fontSize: 11 }}
                  tickFormatter={(val) => {
                    if (!val) return '';
                    const [y, m, d] = val.split('-');
                    return `${d}/${m}`;
                  }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: 'var(--text-tertiary)', fontSize: 11 }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="quantidade"
                  stroke="var(--accent-blue)"
                  strokeWidth={2}
                  fill="url(#colorQtd)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card variant="elevated">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600 }}>Top Estados</h3>
            <span className="text-xs text-secondary">por nº de licitações</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
            {rankEstados.map((est, idx) => (
              <div key={est.uf}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                    <MapPin size={14} style={{ color: 'var(--text-tertiary)' }} />
                    <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>{est.uf}</span>
                  </div>
                  <span className="text-sm text-secondary">{est.total_licitacoes.toLocaleString('pt-BR')}</span>
                </div>
                <div style={{
                  height: 6,
                  borderRadius: 3,
                  background: 'var(--panel-border)',
                  overflow: 'hidden',
                }}>
                  <div style={{
                    height: '100%',
                    width: `${(est.total_licitacoes / maxEstado) * 100}%`,
                    borderRadius: 3,
                    background: idx === 0
                      ? 'var(--gradient-primary)'
                      : 'var(--accent-blue)',
                    opacity: 1 - idx * 0.12,
                    transition: 'width 0.6s ease-out',
                  }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
