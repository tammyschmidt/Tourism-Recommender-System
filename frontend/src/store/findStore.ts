import { create } from 'zustand';

interface FinderState {
  locationQuery: string;
  selectedCategories: string[];
  selectedCategory: string;
  weights: {
    categories: number;
    category: number;
  };
  setLocationQuery: (query: string) => void;
  toggleCategory: (category: string) => void;
  setSelectedCategory: (category: string) => void;
  setWeight: (key: 'categories' | 'category', value: number) => void;
  search: () => void;
}

export const useFinderStore = create<FinderState>((set, get) => ({
  locationQuery: '',
  selectedCategories: [],
  selectedCategory: 'any',
  weights: {
    categories: 50,
    category: 50,
  },

  setLocationQuery: (query) => set({ locationQuery: query }),

  setSelectedCategory: (category) => set({ selectedCategory: category }),

  toggleCategory: (category) => set((state) => {
    const isSelected = state.selectedCategories.includes(category);
    return {
      selectedCategories: isSelected
        ? state.selectedCategories.filter(c => c !== category)
        : [...state.selectedCategories, category],
    };
  }),

  setWeight: (key, value) => set((state) => ({
    weights: {
      ...state.weights,
      [key]: value,
    },
  })),

  search: () => {
    const { locationQuery, selectedCategories, selectedCategory, weights } = get();

    console.log("--- SUCHE GESTARTET ---");
    console.log("Ort:", locationQuery);
    console.log("Kategorien:", selectedCategories);
    console.log("Kategorie:", selectedCategory);
    console.log("Gewichtung:", weights);
    
    alert('Suchkriterien wurden in der Konsole ausgegeben! (Drücke F12)');
  },
}));