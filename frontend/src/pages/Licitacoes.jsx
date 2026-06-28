import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { FilterPanel } from '../components/ui/FilterPanel';
import { Pagination } from '../components/ui/Pagination';
import { EmptyState } from '../components/ui/EmptyState';
import { SkeletonRow } from '../components/ui/Skeleton';
import { Search, ExternalLink, Calendar, Building2 } from 'lucide-react';

const INITIAL_FILTERS = {
  uf: '', modalidade: '', situacao: '', sort: '', valor_minimo: '', valor_maximo: '', data_inicio: '', data_fim: ''
};

const PAGE_SIZE = 10;

const formatCurrency = (val) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

const formatDate = (dateStr) => {
  if (!dateStr) return null;
  return new Date(dateStr).toLocaleDateString('pt-BR');
};

const SITUACAO_COLOR = {
  'Aberta': 'green',
  'Encerrada': 'red',
  'Suspensa': 'orange',
  'Revogada': 'purple',
};

export const Licitacoes = () => {
  const [licitacoes, setLicitacoes] = useState([]);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState(INITIAL_FILTERS);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchLicitacoes = useCallback(async (searchTerm, currentFilters, currentPage) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('page', currentPage);
      params.set('page_size', PAGE_SIZE);

      if (searchTerm) params.set('q', searchTerm);
      if (currentFilters.uf) params.set('uf', currentFilters.uf);
      if (currentFilters.modalidade) params.set('modalidade', currentFilters.modalidade);
      if (currentFilters.situacao) params.set('situacao', currentFilters.situacao);
      if (currentFilters.sort) params.set('sort', currentFilters.sort);
      if (currentFilters.valor_minimo) params.set('valor_minimo', currentFilters.valor_minimo);
      if (currentFilters.valor_maximo) params.set('valor_maximo', currentFilters.valor_maximo);
      if (currentFilters.data_inicio) params.set('data_inicio', currentFilters.data_inicio);
      if (currentFilters.data_fim) params.set('data_fim', currentFilters.data_fim);

      const res = await api.get(`/licitacoes?${params.toString()}`);
      setLicitacoes(res.data.data);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Erro ao buscar licitações:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLicitacoes(search, filters, page);
  }, [page]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLicitacoes(search, filters, 1);
  };

  const handleApplyFilters = () => {
    setPage(1);
    fetchLicitacoes(search, filters, 1);
  };

  const handleClearFilters = () => {
    setFilters(INITIAL_FILTERS);
    setPage(1);
    fetchLicitacoes(search, INITIAL_FILTERS, 1);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      <div className="page-header">
        <h1>Licitações</h1>
        <p>Pesquise e filtre licitações ativas em todo o país. {total > 0 && <span style={{ color: 'var(--accent-blue)' }}>{total.toLocaleString('pt-BR')} resultados</span>}</p>
      </div>

      <Card style={{ marginBottom: '1rem', padding: '1rem 1.25rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.75rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '0.875rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
            <input
              type="text"
              className="input"
              placeholder="Buscar por objeto, órgão, número..."
              style={{ paddingLeft: '2.75rem' }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Buscando...' : 'Pesquisar'}
          </button>
        </form>
      </Card>

      <FilterPanel
        filters={filters}
        onFilterChange={setFilters}
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
      />

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)
        ) : licitacoes.length === 0 ? (
          <Card><EmptyState title="Nenhuma licitação encontrada" description="Tente ajustar os filtros ou o termo de busca." /></Card>
        ) : (
          licitacoes.map((lic, idx) => (
            <Link key={lic.id} to={`/licitacoes/${lic.id}`} style={{ textDecoration: 'none' }}>
              <Card
                variant="elevated"
                style={{
                  display: 'flex', flexDirection: 'column', gap: '0.75rem',
                  animationDelay: `${idx * 0.03}s`,
                  animation: 'fadeInUp 0.3s ease-out both',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                      <Building2 size={14} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                      <span style={{ fontWeight: 600, fontSize: '0.9375rem' }} className="truncate">{lic.orgao?.nome}</span>
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                      {lic.numero_controle} {lic.modalidade && `• ${lic.modalidade}`}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontWeight: 700, color: lic.valor_estimado ? 'var(--accent-green)' : 'var(--text-tertiary)', fontSize: '0.9375rem' }}>
                      {lic.valor_estimado ? formatCurrency(lic.valor_estimado) : 'Não informado'}
                    </div>
                    {lic.data_publicacao && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', justifyContent: 'flex-end', marginTop: '0.25rem' }}>
                        <Calendar size={12} style={{ color: 'var(--text-tertiary)' }} />
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{formatDate(lic.data_publicacao)}</span>
                      </div>
                    )}
                  </div>
                </div>

                <p style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem', lineHeight: 1.5 }} className="truncate">
                  {lic.objeto}
                </p>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <Badge color={SITUACAO_COLOR[lic.situacao] || 'blue'}>{lic.situacao}</Badge>
                  {lic.orgao?.uf && <Badge color="purple">{lic.orgao.uf}</Badge>}
                  <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--accent-blue)', fontSize: '0.75rem' }}>
                    <span>Ver detalhes</span>
                    <ExternalLink size={12} />
                  </div>
                </div>
              </Card>
            </Link>
          ))
        )}
      </div>

      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </div>
  );
};
