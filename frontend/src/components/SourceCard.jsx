export const SourceCard = ({ source }) => (
  <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 my-2 text-sm text-gray-300">
    <div className="flex items-center gap-2 mb-2">
      <span className="bg-blue-900/50 text-blue-400 px-2 py-1 rounded-md text-xs font-semibold">
        📖 {source.source_file} · p.{source.page}
      </span>
      <span className="text-gray-500 text-xs">
        {(source.relevance_score * 100).toFixed(0)}% match
      </span>
    </div>
    <p className="italic">"{source.content_preview}..."</p>
  </div>
);
