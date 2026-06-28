import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Card } from '../components/ui/Card';
import { Tabs } from '../components/ui/Tabs';
import { SkeletonRow } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import {
  Building2, Users, MapPin, Layers,
  Trophy, Medal
} from 'lucide-react';

const formatCurrency = (val) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

const MEDAL_COLORS = ['#FFD700', '#C0C0C0', '#CD7F32'];

const RankRow = ({ index, label, sublabel, value, displayValue, maxValue }) => {
  const pct = maxValue > 0 ? (value / maxValue) * 100 : 0;

  return (
    <div style={{
      padding: '0.875rem 0',
      borderBottom: '1px solid var(--panel-border)',
      animation: 'fadeInUp 0.3s ease-out both',
      animationDelay: `${index * 0.04}s`,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: 0 }}>
          {index < 3 ? (
            <div style={{
              width: 28, height: 28, borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: `${MEDAL_COLORS[index]}15`,
              flexShrink: 0,
            }}>
              <Trophy size={14} style={{ color: MEDAL_COLORS[index] }} />
            </div>
          ) : (
            <div style={{
              width: 28, height: 28, borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'var(--panel-border)',
              color: 'var(--text-tertiary)',
              fontSize: '0.75rem', fontWeight: 700,
              flexShrink: 0,
            }}>
              {index + 1}
            </div>
          )}
          <div style={{ minWidth: 0 }}>
            <div style={{ fontWeight: 500, fontSize: '0.875rem' }} className="truncate">{label}</div>
            {sublabel && <div className="text-xs text-secondary">{sublabel}</div>}
          </div>
        </div>
        <span style={{ fontWeight: 600, fontSize: '0.875rem', flexShrink: 0, marginLeft: '1rem' }}>{displayValue || value}</span>
      </div>
      <div style={{ height: 4, borderRadius: 2, background: 'var(--panel-border)', overflow: 'hidden' }}>
        <div style={{
          height: '100%',
          width: `${pct}%`,
          borderRadius: 2,
          background: index < 3 ? 'var(--gradient-primary)' : 'var(--accent-blue)',
          opacity: Math.max(0.4, 1 - index * 0.08),
          transition: 'width 0.8s ease-out',
        }} />
      </div>
    </div>
  );
};

export const Rankings = () => {
  const [orgaos, setOrgaos] = useState([]);
  const [fornecedores, setFornecedores] = useState([]);
  const [estados, setEstados] = useState([]);
  const [modalidades, setModalidades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('orgaos');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [orgRes, fornRes, estRes, modRes] = await Promise.all([
          api.get('/ranking/orgaos?limit=10'),
          api.get('/ranking/fornecedores/volume?limit=10'),
          api.get('/ranking/estados?limit=10&t=1'),
          api.get('/ranking/modalidades?limit=10'),
        ]);
        setOrgaos(orgRes.data);
        setFornecedores(fornRes.data);
        setEstados(estRes.data);
        setModalidades(modRes.data);
      } catch (err) {
        console.error('Erro ao carregar rankings:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const tabs = [
    { key: 'orgaos', label: 'Órgãos', icon: <Building2 size={14} /> },
    { key: 'fornecedores', label: 'Fornecedores', icon: <Users size={14} /> },
    { key: 'estados', label: 'Estados', icon: <MapPin size={14} /> },
    { key: 'modalidades', label: 'Modalidades', icon: <Layers size={14} /> },
  ];

  const renderLoading = () => (
    Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
  );

  return (
    <div>
      <div className="page-header">
        <h1>Rankings</h1>
        <p>Os maiores compradores, fornecedores e tendências do governo.</p>
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'orgaos' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Top Órgãos Compradores
          </h3>
          <p className="text-xs text-secondary" style={{ marginBottom: '1rem' }}>
            Ranking por número total de licitações publicadas
          </p>
          {loading ? renderLoading() : orgaos.length === 0 ? (
            <EmptyState title="Sem dados" />
          ) : (
            orgaos.map((org, idx) => (
              <RankRow
                key={org.orgao_id}
                index={idx}
                label={org.nome}
                sublabel={`${org.total_licitacoes.toLocaleString('pt-BR')} licitações`}
                value={org.total_licitacoes}
                displayValue={org.total_licitacoes.toLocaleString('pt-BR')}
                maxValue={orgaos[0]?.total_licitacoes || 1}
              />
            ))
          )}
        </Card>
      )}

      {activeTab === 'fornecedores' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Top Fornecedores por Volume
          </h3>
          <p className="text-xs text-secondary" style={{ marginBottom: '1rem' }}>
            Ranking por volume total contratado (R$)
          </p>
          {loading ? renderLoading() : fornecedores.length === 0 ? (
            <EmptyState title="Sem dados" />
          ) : (
            fornecedores.map((forn, idx) => (
              <RankRow
                key={forn.fornecedor_id}
                index={idx}
                label={forn.nome}
                sublabel={`CNPJ: ${forn.ni} • ${forn.quantidade_contratos} contratos`}
                value={forn.volume_total}
                displayValue={formatCurrency(forn.volume_total)}
                maxValue={fornecedores[0]?.volume_total || 1}
              />
            ))
          )}
        </Card>
      )}

      {activeTab === 'estados' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Ranking por Estado (UF)
          </h3>
          <p className="text-xs text-secondary" style={{ marginBottom: '1rem' }}>
            Estados com mais licitações publicadas
          </p>
          {loading ? renderLoading() : estados.length === 0 ? (
            <EmptyState title="Sem dados" />
          ) : (
            estados.map((est, idx) => (
              <RankRow
                key={est.uf}
                index={idx}
                label={est.uf}
                sublabel={`${est.total_licitacoes.toLocaleString('pt-BR')} licitações`}
                value={est.total_licitacoes}
                displayValue={est.total_licitacoes.toLocaleString('pt-BR')}
                maxValue={estados[0]?.total_licitacoes || 1}
              />
            ))
          )}
        </Card>
      )}

      {activeTab === 'modalidades' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Ranking por Modalidade
          </h3>
          <p className="text-xs text-secondary" style={{ marginBottom: '1rem' }}>
            Modalidades de licitação mais utilizadas
          </p>
          {loading ? renderLoading() : modalidades.length === 0 ? (
            <EmptyState title="Sem dados" />
          ) : (
            modalidades.map((mod, idx) => (
              <RankRow
                key={mod.modalidade}
                index={idx}
                label={mod.modalidade}
                sublabel={`${mod.total_licitacoes.toLocaleString('pt-BR')} licitações`}
                value={mod.total_licitacoes}
                displayValue={mod.total_licitacoes.toLocaleString('pt-BR')}
                maxValue={modalidades[0]?.total_licitacoes || 1}
              />
            ))
          )}
        </Card>
      )}
    </div>
  );
};
