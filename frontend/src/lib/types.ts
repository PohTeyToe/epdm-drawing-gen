export type DisciplineCode = "E" | "M" | "S" | "O";

export interface Drawing {
  id: string;
  prefix: string;
  discipline: DisciplineCode;
  discipline_name: string;
  sequence: number;
  revision: string;
  drawing_type: string;
  title: string;
  vault_path: string;
  created_at: string;
  is_new: boolean;
}

export interface DrawingListResponse {
  items: Drawing[];
  total: number;
  page: number;
  size: number;
}

export interface DisciplineOption {
  code: DisciplineCode;
  name: string;
}

export interface GenerateRequest {
  project_code: string;
  discipline: DisciplineCode;
  revision: string;
  drawing_type: string;
  title?: string;
}
