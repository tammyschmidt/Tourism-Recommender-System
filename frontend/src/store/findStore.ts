import { create } from 'zustand';

interface FinderState {
  locationQuery: string;
  selectedCuisines: string[];
  selectedSetting: string;
  weights: {
    cuisine: number;
    setting: number;
  };
  setLocationQuery: (query: string) => void;
  toggleCuisine: (cuisine: string) => void;
  setSelectedSetting: (setting: string) => void;
  setWeight: (key: 'cuisine' | 'setting', value: number) => void;
  search: () => void;
}

export const useFinderStore = create<FinderState>((set, get) => ({
  locationQuery: '',
  selectedCuisines: [],
  selectedSetting: 'any',
  weights: {
    cuisine: 50,
    setting: 50,
  },

  setLocationQuery: (query) => set({ locationQuery: query }),

  setSelectedSetting: (setting) => set({ selectedSetting: setting }),

  toggleCuisine: (cuisine) => set((state) => {
    const isSelected = state.selectedCuisines.includes(cuisine);
    return {
      selectedCuisines: isSelected
        ? state.selectedCuisines.filter(c => c !== cuisine)
        : [...state.selectedCuisines, cuisine],
    };
  }),

  setWeight: (key, value) => set((state) => ({
    weights: {
      ...state.weights,
      [key]: value,
    },
  })),

  search: () => {
    const { locationQuery, selectedCuisines, selectedSetting, weights } = get();

    console.log("--- SUCHE GESTARTET ---");
    console.log("Ort:", locationQuery);
    console.log("Küchen:", selectedCuisines);
    console.log("Ambiente:", selectedSetting);
    console.log("Gewichtung:", weights);
    
    alert('Suchkriterien wurden in der Konsole ausgegeben! (Drücke F12)');
  },
}));