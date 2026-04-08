#!/bin/bash

# Stop all MCP agents

echo "🛑 Stopping MCP Agents..."
echo ""

if [ -f "mcp_agents/.agent_pids" ]; then
    PIDS=$(cat mcp_agents/.agent_pids)
    echo "Found agent PIDs: $PIDS"
    
    for PID in $PIDS; do
        if ps -p $PID > /dev/null; then
            echo "Stopping process $PID..."
            kill $PID
        else
            echo "Process $PID not running"
        fi
    done
    
    rm mcp_agents/.agent_pids
    echo ""
    echo "✅ All agents stopped!"
else
    echo "⚠️  No PID file found. Searching for agent processes..."
    
    # Find and kill Python processes running agents
    pkill -f "orchestrator/agent.py"
    pkill -f "fixer/agent.py"
    pkill -f "reporter/agent.py"
    
    echo "✅ Agent processes terminated"
fi
