import api from './api';

export const syncService = {
  sincronizarPNCP: async (dataInicial, dataFinal) => {
    const response = await api.post('/sincronizar', {
      data_inicial: dataInicial,
      data_final: dataFinal,
    });
    return response.data;
  },
};
