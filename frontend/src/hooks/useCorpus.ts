import { useEffect, useState } from "react";

export interface CorpusDocument {
  name: string;
  content: string;
}

const API_URL = import.meta.env.VITE_API_URL ?? "";

let cache: CorpusDocument[] | null = null;
let pending: Promise<CorpusDocument[]> | null = null;

function fetchCorpus(): Promise<CorpusDocument[]> {
  if (cache) return Promise.resolve(cache);
  if (!pending) {
    pending = fetch(`${API_URL}/api/corpus`)
      .then((res) => res.json())
      .then((data: { documents: CorpusDocument[] }) => {
        cache = data.documents;
        return cache;
      })
      .catch(() => {
        pending = null;
        return [];
      });
  }
  return pending;
}

export function useCorpus(): CorpusDocument[] {
  const [documents, setDocuments] = useState<CorpusDocument[]>(cache ?? []);

  useEffect(() => {
    let mounted = true;
    fetchCorpus().then((docs) => {
      if (mounted) setDocuments(docs);
    });
    return () => {
      mounted = false;
    };
  }, []);

  return documents;
}
