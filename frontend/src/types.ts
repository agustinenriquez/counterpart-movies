export interface Movie {
    tconst: string;
    title: string;
    original_title: string;
    year: string;
    runtime: string;
    genre: string;
    rating: number;
  }

  export interface Principal {
    id: number;
    category: string;
    characters: string[];
    tconst: string;
    nconst: string;
  }

  export interface Name {
    nconst: string;
    name: string;
    birth_year: string;
    death_year: string | null;
    primary_professions: string;
  }

  export interface MoviesApiResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Movie[];
  }
