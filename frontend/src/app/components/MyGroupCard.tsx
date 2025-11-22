"use client";

interface MyGroupCardProps {
  title: string;
  description: string;
  status: "Active" | "Inactive" | "Paused";
  joinedDate: string;
  myPerformance: string;
  roi: string;
  totalTradesCopied: number;
  winRate: string;
  lastTrade: string;
  onViewDetails: () => void;
  onLeaveGroup: () => void;
}

export default function MyGroupCard({
  title,
  description,
  status,
  joinedDate,
  myPerformance,
  roi,
  totalTradesCopied,
  winRate,
  lastTrade,
  onViewDetails,
  onLeaveGroup,
}: MyGroupCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active":
        return "bg-green-100 text-green-800";
      case "Inactive":
        return "bg-gray-100 text-gray-800";
      case "Paused":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
          <p className="text-gray-600 mb-3">{description}</p>
        </div>
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status)}`}>
          {status}
        </span>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-500 mb-1">Joined</div>
          <div className="text-sm font-semibold text-gray-900">{joinedDate}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500 mb-1">My Performance</div>
          <div className="text-sm font-semibold text-green-600">{myPerformance}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500 mb-1">ROI</div>
          <div className="text-sm font-semibold text-green-600">{roi}</div>
        </div>
      </div>

      {/* Additional Details */}
      <div className="space-y-2 mb-6">
        <div className="text-sm text-gray-600">
          Total Trades Copied: <span className="font-semibold text-gray-900">{totalTradesCopied}</span>
        </div>
        <div className="text-sm text-gray-600">
          Win Rate: <span className="font-semibold text-gray-900">{winRate}</span>
        </div>
        <div className="text-sm text-gray-600">
          Last Trade: <span className="font-semibold text-gray-900">{lastTrade}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={onViewDetails}
          className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-semibold hover:bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          View Details
        </button>
        <button
          onClick={onLeaveGroup}
          className="flex-1 border border-red-300 text-red-600 py-2 px-4 rounded-lg font-semibold hover:bg-red-50 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Leave Group
        </button>
      </div>
    </div>
  );
}
