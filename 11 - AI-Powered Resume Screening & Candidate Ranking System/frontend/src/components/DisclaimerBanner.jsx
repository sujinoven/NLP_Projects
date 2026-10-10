import React from 'react';
import { Info } from 'lucide-react';

export default function DisclaimerBanner({ text }) {
  return (
    <div className="glass-panel p-4 mb-8 border-indigo-500/20 bg-indigo-500/[0.03] text-xs text-indigo-300/90 flex items-center gap-3">
      <Info className="w-5 h-5 text-indigo-400 flex-shrink-0" />
      <p>
        <strong>Note:</strong> {text || "Similarity scores support human review and decision-making; they do not guarantee or verify that every candidate requirement is fully satisfied."}
      </p>
    </div>
  );
}
