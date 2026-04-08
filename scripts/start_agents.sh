#!/bin/bash

# Start all MCP agents in separate processes

echo "🤖 Starting MCP Agents..."
echo ""

# Check if virtual environment exists
if [ ! -d "mcp_agents/venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
cd mcp_agents
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Start Orchestrator Agent (Port 8001)
echo "🎯 Starting Orchestrator Agent on port 8001..."
python orchestrator/agent.py &
ORCHESTRATOR_PID=$!
echo "   PID: $ORCHESTRATOR_PID"

# Wait a bit
sleep 2

# Start Fixer Agent (Port 8002)
echo "🔧 Starting Fixer Agent on port 8002..."
python fixer/agent.py &
FIXER_PID=$!
echo "   PID: $FIXER_PID"

# Wait a bit
sleep 2

# Start Reporter Agent (Port 8003)
echo "📝 Starting Reporter Agent on port 8003..."
python reporter/agent.py &
REPORTER_PID=$!
echo "   PID: $REPORTER_PID"

echo ""
echo "✅ All agents started!"
echo ""
echo "Agent PIDs:"
echo "   Orchestrator: $ORCHESTRATOR_PID"
echo "   Fixer: $FIXER_PID"
echo "   Reporter: $REPORTER_PID"
echo ""
echo "To stop agents, run:"
echo "   kill $ORCHESTRATOR_PID $FIXER_PID $REPORTER_PID"
echo ""
echo "Or save PIDs to file:"
echo "   echo \"$ORCHESTRATOR_PID $FIXER_PID $REPORTER_PID\" > .agent_pids"
echo ""

# Save PIDs to file
echo "$ORCHESTRATOR_PID $FIXER_PID $REPORTER_PID" > .agent_pids

# Keep script running
wait
