#!/usr/bin/env python3
"""
LSP Skills Self-Improvement System

Tracks usage patterns and provides analytics for optimizing LSP skills and agents.
Generates weekly reports and suggests improvements.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import os


class LSPUsageTracker:
    """Tracks LSP skill/agent usage and effectiveness."""
    
    def __init__(self):
        self.log_file = Path.home() / ".claude" / "lsp_usage_log.json"
        self.metrics_file = Path.home() / ".claude" / "lsp_metrics.json"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_usage(self, skill_name: str, operation: str, success: bool, 
                 duration_seconds: float, symbols_processed: int = 1):
        """Log a single LSP operation."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "skill": skill_name,
            "operation": operation,  # go-to-definition, find-references, hover
            "success": success,
            "duration": duration_seconds,
            "symbols_processed": symbols_processed
        }
        
        logs = self.load_logs()
        logs.append(entry)
        self.save_logs(logs)
    
    def load_logs(self) -> List[Dict[str, Any]]:
        """Load existing logs."""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_logs(self, logs: List[Dict[str, Any]]):
        """Save logs to file."""
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly usage analytics."""
        logs = self.load_logs()
        if not logs:
            return {"message": "No usage data available"}
        
        # Filter last 7 days
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        recent_logs = [
            log for log in logs 
            if datetime.datetime.fromisoformat(log["timestamp"]) > week_ago
        ]
        
        if not recent_logs:
            return {"message": "No data from last 7 days"}
        
        # Calculate metrics
        total_operations = len(recent_logs)
        successful_operations = sum(1 for log in recent_logs if log["success"])
        success_rate = successful_operations / total_operations if total_operations > 0 else 0
        
        # Group by skill
        skill_usage = {}
        for log in recent_logs:
            skill = log["skill"]
            if skill not in skill_usage:
                skill_usage[skill] = {"count": 0, "success": 0, "avg_duration": 0}
            skill_usage[skill]["count"] += 1
            if log["success"]:
                skill_usage[skill]["success"] += 1
            skill_usage[skill]["avg_duration"] += log["duration"]
        
        # Calculate averages and success rates per skill
        for skill, data in skill_usage.items():
            data["success_rate"] = data["success"] / data["count"]
            data["avg_duration"] = data["avg_duration"] / data["count"]
        
        # Group by operation type
        operation_usage = {}
        for log in recent_logs:
            op = log["operation"]
            operation_usage[op] = operation_usage.get(op, 0) + 1
        
        # Identify patterns and recommendations
        recommendations = self.generate_recommendations(skill_usage, operation_usage)
        
        report = {
            "period": "Last 7 days",
            "generated_at": datetime.datetime.now().isoformat(),
            "summary": {
                "total_operations": total_operations,
                "success_rate": success_rate,
                "unique_skills_used": len(skill_usage),
                "most_used_operation": max(operation_usage.items(), key=lambda x: x[1])[0] if operation_usage else None
            },
            "skill_breakdown": skill_usage,
            "operation_breakdown": operation_usage,
            "recommendations": recommendations
        }
        
        self.save_metrics(report)
        return report
    
    def generate_recommendations(self, skill_usage: Dict, operation_usage: Dict) -> List[str]:
        """Generate improvement recommendations based on usage patterns."""
        recommendations = []
        
        # Check for low success rates
        for skill, data in skill_usage.items():
            if data["success_rate"] < 0.8:
                recommendations.append(
                    f"⚠️ {skill} has low success rate ({data['success_rate']:.1%}). "
                    f"Consider refining error handling or disambiguation logic."
                )
            
            if data["avg_duration"] > 5.0:
                recommendations.append(
                    f"⏱️ {skill} operations are slow ({data['avg_duration']:.1f}s avg). "
                    f"Consider adding 'if too many references, filter by path' rules."
                )
        
        # Check for operation imbalances
        if "find-references" in operation_usage and operation_usage["find-references"] > 20:
            recommendations.append(
                "🔍 High find-references usage detected. Consider implementing "
                "reference filtering or batching strategies."
            )
        
        # Check for unused skills
        if len(skill_usage) < 3:
            recommendations.append(
                "📚 Low skill diversity. Try using dependency-analyzer "
                "or type-checker skills for comprehensive analysis."
            )
        
        if not recommendations:
            recommendations.append("✅ Usage patterns look optimal!")
        
        return recommendations
    
    def save_metrics(self, report: Dict[str, Any]):
        """Save metrics report."""
        with open(self.metrics_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted report."""
        print("📊 LSP Skills Weekly Report")
        print("=" * 40)
        
        if "message" in report:
            print(f"ℹ️  {report['message']}")
            return
        
        summary = report["summary"]
        print(f"📈 Summary:")
        print(f"  Total operations: {summary['total_operations']}")
        print(f"  Success rate: {summary['success_rate']:.1%}")
        print(f"  Skills used: {summary['unique_skills_used']}")
        print(f"  Most used operation: {summary['most_used_operation']}")
        
        print("\n🎯 Skill Performance:")
        for skill, data in report["skill_breakdown"].items():
            print(f"  {skill}:")
            print(f"    Usage: {data['count']} times")
            print(f"    Success: {data['success_rate']:.1%}")
            print(f"    Avg duration: {data['avg_duration']:.1f}s")
        
        print("\n🔧 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")


def main():
    """Generate and display weekly LSP usage report."""
    tracker = LSPUsageTracker()
    report = tracker.generate_weekly_report()
    tracker.print_report(report)
    
    print(f"\n📁 Detailed metrics saved to: {tracker.metrics_file}")
    print("💡 Use this data to refine skill prompts and agent descriptions")


if __name__ == "__main__":
    main()