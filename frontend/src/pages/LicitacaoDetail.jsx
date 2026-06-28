import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Tabs } from '../components/ui/Tabs';
import { Timeline } from '../components/ui/Timeline';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import {
  ArrowLeft, Building2, Calendar, DollarSign, FileText,
  Package, Paperclip, History, ExternalLink
} from 'lucide-react';

const formatCurrency = (val) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('pt-BR', {
    day: '2-digit', month: 'long', year: 'numeric',
  });
};

const getPncpUrl = (numeroControle) => {
  if (numeroControle) {
    // Divide por '-' ou '/'
    const parts = numeroControle.split(/[-/]/);
    if (parts.length >= 4) {
      const cnpj = parts[0];
      const sequencial = parseInt(parts[2], 10);
      const ano = parts[3];
      return `https://pncp.gov.br/app/editais/${cnpj}/${ano}/${sequencial}`;
    } else if (parts.length === 3) {
      const cnpj = parts[0];
      const sequencial = parseInt(parts[1], 10);
      const ano = parts[2];
      return `https://pncp.gov.br/app/editais/${cnpj}/${ano}/${sequencial}`;
    }
  }
  return 'https://pncp.gov.br/app/editais/';
};

export const LicitacaoDetail = () => {
  const { id } = useParams();
  const [licitacao, setLicitacao] = useState(null);
  const [itens, setItens] = useState([]);
  const [arquivos, setArquivos] = useState([]);
  const [historico, setHistorico] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [licRes, itensRes, arqRes, histRes] = await Promise.all([
          api.get(`/licitacoes/${id}`),
          api.get(`/licitacoes/${id}/itens`).catch(() => ({ data: [] })),
          api.get(`/licitacoes/${id}/arquivos`).catch(() => ({ data: [] })),
          api.get(`/licitacoes/${id}/historico`).catch(() => ({ data: [] })),
        ]);
        setLicitacao(licRes.data);
        setItens(itensRes.data);
        setArquivos(arqRes.data);
        setHistorico(histRes.data);
      } catch (err) {
        console.error('Erro ao carregar detalhes:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [id]);

  if (loading) {
    return (
      <div>
        <Skeleton width="30%" height="1.5rem" />
        <div style={{ marginTop: '1.5rem' }}>
          <Skeleton height="200px" borderRadius="var(--radius-lg)" />
        </div>
      </div>
    );
  }

  if (!licitacao) {
    return (
      <div>
        <Link to="/licitacoes" className="btn btn-ghost" style={{ marginBottom: '1rem' }}>
          <ArrowLeft size={16} /> Voltar
        </Link>
        <Card>
          <EmptyState title="Licitação não encontrada" description="O registro pode ter sido removido ou o link é inválido." />
        </Card>
      </div>
    );
  }

  const tabs = [
    { key: 'info', label: 'Informações', icon: <FileText size={14} /> },
    { key: 'itens', label: 'Itens', icon: <Package size={14} />, count: itens.length },
    { key: 'arquivos', label: 'Arquivos', icon: <Paperclip size={14} />, count: arquivos.length },
    { key: 'historico', label: 'Histórico', icon: <History size={14} />, count: historico.length },
  ];

  return (
    <div>
      <Link to="/licitacoes" className="btn btn-ghost" style={{ marginBottom: '1.25rem', padding: '0.375rem 0' }}>
        <ArrowLeft size={16} /> Voltar para busca
      </Link>

      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h1>{licitacao.numero_controle || 'Licitação'}</h1>
          <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Building2 size={14} /> {licitacao.orgao?.nome}
          </p>
        </div>
        <a
          href={getPncpUrl(licitacao.numero_controle)}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}
        >
          Ver mais detalhes <ExternalLink size={16} />
        </a>
      </div>

      <div className="grid grid-cols-4" style={{ marginBottom: '1.5rem' }}>
        <Card>
          <div className="text-xs text-secondary" style={{ marginBottom: '0.375rem' }}>Modalidade</div>
          <div style={{ fontWeight: 600, fontSize: '0.9375rem' }}>{licitacao.modalidade || '—'}</div>
        </Card>
        <Card>
          <div className="text-xs text-secondary" style={{ marginBottom: '0.375rem' }}>Valor Estimado</div>
          <div style={{ fontWeight: 700, color: 'var(--accent-green)', fontSize: '0.9375rem' }}>
            {licitacao.valor_estimado ? formatCurrency(licitacao.valor_estimado) : '—'}
          </div>
        </Card>
        <Card>
          <div className="text-xs text-secondary" style={{ marginBottom: '0.375rem' }}>Situação</div>
          <Badge color="blue">{licitacao.situacao || '—'}</Badge>
        </Card>
        <Card>
          <div className="text-xs text-secondary" style={{ marginBottom: '0.375rem' }}>Publicação</div>
          <div style={{ fontWeight: 500, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
            <Calendar size={13} style={{ color: 'var(--text-tertiary)' }} />
            {formatDate(licitacao.data_publicacao)}
          </div>
        </Card>
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'info' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.75rem' }}>Objeto da Licitação</h3>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: '0.875rem' }}>
            {licitacao.objeto}
          </p>

          {licitacao.data_encerramento && (
            <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--panel-border)' }}>
              <span className="text-xs text-secondary">Data de encerramento: </span>
              <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>{formatDate(licitacao.data_encerramento)}</span>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'itens' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          {itens.length === 0 ? (
            <EmptyState icon={Package} title="Nenhum item registrado" description="Este edital não possui itens detalhados." />
          ) : (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Descrição</th>
                    <th style={{ textAlign: 'right' }}>Qtd</th>
                    <th style={{ textAlign: 'right' }}>Valor Unit.</th>
                    <th style={{ textAlign: 'right' }}>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {itens.map((item) => (
                    <tr key={item.id}>
                      <td>{item.descricao}</td>
                      <td style={{ textAlign: 'right' }}>{item.quantidade}</td>
                      <td style={{ textAlign: 'right' }}>
                        {item.valor_unitario != null ? formatCurrency(item.valor_unitario) : '—'}
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600 }}>
                        {item.valor_total != null ? formatCurrency(item.valor_total) : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'arquivos' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          {arquivos.length === 0 ? (
            <EmptyState icon={Paperclip} title="Nenhum arquivo anexo" description="Não foram encontrados documentos para esta licitação." />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {arquivos.map((arq) => (
                <a
                  key={arq.id}
                  href={arq.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.75rem 1rem',
                    border: '1px solid var(--panel-border)',
                    borderRadius: 'var(--radius-md)',
                    transition: 'all 0.15s',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--panel-border-hover)'; e.currentTarget.style.background = 'rgba(255,255,255,0.02)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--panel-border)'; e.currentTarget.style.background = 'transparent'; }}
                >
                  <Paperclip size={16} style={{ color: 'var(--accent-blue)', flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 500, fontSize: '0.875rem' }} className="truncate">{arq.nome}</div>
                    {arq.tipo && <div className="text-xs text-secondary">{arq.tipo}</div>}
                  </div>
                  <ExternalLink size={14} style={{ color: 'var(--text-tertiary)', flexShrink: 0 }} />
                </a>
              ))}
            </div>
          )}
        </Card>
      )}

      {activeTab === 'historico' && (
        <Card style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          {historico.length === 0 ? (
            <EmptyState icon={History} title="Sem histórico registrado" description="Nenhuma fase foi registrada para esta licitação." />
          ) : (
            <Timeline items={historico} />
          )}
        </Card>
      )}
    </div>
  );
};
