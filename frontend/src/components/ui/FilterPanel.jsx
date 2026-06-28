import React, { useState } from 'react';
import { ChevronDown, Filter } from 'lucide-react';
import './FilterPanel.css';

export const FilterPanel = ({ filters, onFilterChange, onApply, onClear }) => {
  const [expanded, setExpanded] = useState(false);

  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const applyPreset = (months) => {
    const today = new Date();
    const start = new Date();
    start.setMonth(today.getMonth() - months);
    
    // Convert to YYYY-MM-DD
    const formatDate = (date) => date.toISOString().split('T')[0];
    
    onFilterChange({
      ...filters,
      data_inicio: formatDate(start),
      data_fim: formatDate(today)
    });
  };

  const activeCount = Object.values(filters).filter((v) => v !== '' && v != null).length;

  return (
    <div className="filter-panel">
      <button
        className="filter-panel__toggle"
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} />
          <span>Filtros avançados</span>
          {activeCount > 0 && (
            <span className="filter-panel__count">{activeCount}</span>
          )}
        </div>
        <ChevronDown
          size={16}
          style={{
            transform: expanded ? 'rotate(180deg)' : 'rotate(0)',
            transition: 'transform 0.2s',
          }}
        />
      </button>

      {expanded && (
        <div className="filter-panel__body">
          <div className="filter-panel__grid">
            
            {/* Linha de Datas */}
            <div className="filter-panel__field" style={{ gridColumn: '1 / -1' }}>
              <label>Período de Publicação</label>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <button 
                  className="btn btn-ghost btn-sm" 
                  onClick={() => applyPreset(1)}
                  style={{ border: '1px solid var(--panel-border)' }}
                >
                  Último Mês
                </button>
                <button 
                  className="btn btn-ghost btn-sm" 
                  onClick={() => applyPreset(3)}
                  style={{ border: '1px solid var(--panel-border)' }}
                >
                  Últimos 3 Meses
                </button>
                
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>De:</span>
                  <input
                    type="date"
                    className="input"
                    style={{ padding: '0.25rem 0.5rem', width: 'auto' }}
                    value={filters.data_inicio || ''}
                    onChange={(e) => handleChange('data_inicio', e.target.value)}
                  />
                  <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Até:</span>
                  <input
                    type="date"
                    className="input"
                    style={{ padding: '0.25rem 0.5rem', width: 'auto' }}
                    value={filters.data_fim || ''}
                    onChange={(e) => handleChange('data_fim', e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="filter-panel__field">
              <label>UF</label>
              <select
                className="select"
                value={filters.uf || ''}
                onChange={(e) => handleChange('uf', e.target.value)}
              >
                <option value="">Todas</option>
                {['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'].map(
                  (uf) => <option key={uf} value={uf}>{uf}</option>
                )}
              </select>
            </div>

            <div className="filter-panel__field">
              <label>Modalidade</label>
              <select
                className="select"
                value={filters.modalidade || ''}
                onChange={(e) => handleChange('modalidade', e.target.value)}
              >
                <option value="">Todas</option>
                <option value="Dispensa">Dispensa</option>
                <option value="Credenciamento">Credenciamento</option>
                <option value="Inexigibilidade">Inexigibilidade</option>
                <option value="Pregão - Eletrônico">Pregão - Eletrônico</option>
                <option value="Pregão - Presencial">Pregão - Presencial</option>
                <option value="Concorrência - Eletrônica">Concorrência - Eletrônica</option>
                <option value="Concorrência - Presencial">Concorrência - Presencial</option>
                <option value="Concurso">Concurso</option>
              </select>
            </div>

            <div className="filter-panel__field">
              <label>Situação</label>
              <select
                className="select"
                value={filters.situacao || ''}
                onChange={(e) => handleChange('situacao', e.target.value)}
              >
                <option value="">Todas</option>
                <option value="Divulgada no PNCP">Divulgada no PNCP</option>
                <option value="Suspensa">Suspensa</option>
                <option value="Revogada">Revogada</option>
                <option value="Anulada">Anulada</option>
              </select>
            </div>

            <div className="filter-panel__field">
              <label>Ordenação</label>
              <select
                className="select"
                value={filters.sort || ''}
                onChange={(e) => handleChange('sort', e.target.value)}
              >
                <option value="">Padrão</option>
                <option value="data_publicacao_desc">Mais recentes</option>
                <option value="data_publicacao_asc">Mais antigas</option>
                <option value="valor_desc">Maior valor</option>
                <option value="valor_asc">Menor valor</option>
              </select>
            </div>

            <div className="filter-panel__field">
              <label>Valor mínimo</label>
              <input
                type="number"
                className="input"
                placeholder="R$ 0"
                value={filters.valor_minimo || ''}
                onChange={(e) => handleChange('valor_minimo', e.target.value)}
              />
            </div>

            <div className="filter-panel__field">
              <label>Valor máximo</label>
              <input
                type="number"
                className="input"
                placeholder="Sem limite"
                value={filters.valor_maximo || ''}
                onChange={(e) => handleChange('valor_maximo', e.target.value)}
              />
            </div>
          </div>

          <div className="filter-panel__actions">
            <button className="btn btn-ghost btn-sm" onClick={onClear}>Limpar</button>
            <button className="btn btn-primary btn-sm" onClick={onApply}>Aplicar filtros</button>
          </div>
        </div>
      )}
    </div>
  );
};

