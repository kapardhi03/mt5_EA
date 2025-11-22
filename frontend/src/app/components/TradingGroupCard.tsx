"use client";

interface TradingGroupCardProps {
  title: string;
  description: string;
  status: "Available" | "Full" | "Closed";
  members: number;
  monthlyROI: string;
  master: string;
  strategy: string;
  riskLevel: "Low" | "Medium" | "High";
  avgTradeDuration: string;
  onJoinGroup: () => void;
}

export default function TradingGroupCard({
  title,
  description,
  status,
  members,
  monthlyROI,
  master,
  strategy,
  riskLevel,
  avgTradeDuration,
  onJoinGroup,
}: TradingGroupCardProps) {
  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "Low":
        return "text-green-600";
      case "Medium":
        return "text-yellow-600";
      case "High":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Available":
        return "bg-green-100 text-green-800";
      case "Full":
        return "bg-yellow-100 text-yellow-800";
      case "Closed":
        return "bg-red-100 text-red-800";
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

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-500 mb-1">Members</div>
          <div className="text-lg font-bold text-gray-900">{members}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500 mb-1">Monthly ROI</div>
          <div className="text-lg font-bold text-teal-600">{monthlyROI}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500 mb-1">Master</div>
          <div className="text-lg font-bold text-gray-900">{master}</div>
        </div>
      </div>

      {/* Strategy Details */}
      <div className="space-y-2 mb-6">
        <div className="text-sm">
          <span className="text-gray-500">Strategy: </span>
          <span className="text-gray-900">{strategy}</span>
        </div>
        <div className="text-sm">
          <span className="text-gray-500">Risk Level: </span>
          <span className={`font-medium ${getRiskLevelColor(riskLevel)}`}>{riskLevel}</span>
        </div>
        <div className="text-sm">
          <span className="text-gray-500">Avg. Trade Duration: </span>
          <span className="text-gray-900">{avgTradeDuration}</span>
        </div>
      </div>

      {/* Join Button */}
      <button
        onClick={onJoinGroup}
        className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
      >
        Join Group
      </button>
    </div>
  );
}
