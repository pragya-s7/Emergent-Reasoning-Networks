import React, { useState, ChangeEvent, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@radix-ui/react-label";
import { Upload, Sparkles } from "lucide-react";
import ReactFlow, { MiniMap, Controls, Background, Node, Edge } from 'reactflow';

// Define types
interface ReasoningResult {
  conclusion?: string;
  reasoningPath?: any[];
  [key: string]: any;
}

interface ValidationResult {
  [key: string]: any;
}

interface ApiResponse {
  reasoning: ReasoningResult | null;
  validation: ValidationResult | null;
  error?: string;
}

export default function KairosFrontend() {
  const [query, setQuery] = useState<string>("");
  const [apiKey, setApiKey] = useState<string>("");
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [knowledgeGraph, setKnowledgeGraph] = useState<any | null>(null);
  const [tab, setTab] = useState<string>("reasoning");
  const [loading, setLoading] = useState<boolean>(false);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (result?.reasoning?.reasoningPath) {
      const path = result.reasoning.reasoningPath;
      const newNodes: Node[] = [];
      const newEdges: Edge[] = [];
      let yPos = 0;

      path.forEach((step, i) => {
        const nodeId = `node-${i}`;
        newNodes.push({
          id: nodeId,
          data: { label: `${step.step}: ${step.inference}` },
          position: { x: 250, y: yPos },
        });
        yPos += 100;

        if (i > 0) {
          newEdges.push({
            id: `edge-${i-1}-${i}`,
            source: `node-${i-1}`,
            target: nodeId,
            animated: true,
          });
        }
      });

      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [result]);


  const handleQuery = async () => {
    if (!apiKey) {
      alert("Please provide an OpenAI API key");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          anthropic_key: apiKey,
          run_validation: true,
          knowledge_graph: knowledgeGraph
        }),
      });
      const data: ApiResponse = await res.json();
      setResult(data);

      if (data.error) {
        alert(`Error: ${data.error}`);
      }
    } catch (err) {
      console.error("Query failed:", err);
      alert("Failed to process query. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleTxtUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      await fetch("/api/ingest", { method: "POST", body: formData });
      alert("TXT file ingested successfully. You can now query the knowledge graph.");
    } catch (err) {
      console.error("Ingestion failed:", err);
    }
  };

  const handleKgUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const kg = JSON.parse(event.target?.result as string);
        setKnowledgeGraph(kg);
        alert("Knowledge graph loaded successfully.");
      } catch (err) {
        console.error("Failed to parse knowledge graph:", err);
        alert("Invalid knowledge graph file.");
      }
    };
    reader.readAsText(file);
  };


  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold tracking-tight">Kairos Reasoning Network</h1>
      <Card className="p-4 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="apiKey">Anthropic API Key</Label>
          <Input
            id="apiKey"
            type="password"
            placeholder="sk-..."
            value={apiKey}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setApiKey(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="query">Query</Label>
          <Textarea
            id="query"
            placeholder="Analyze the financial risks in the knowledge graph..."
            value={query}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-4">
          <Button onClick={handleQuery} disabled={loading}>
            <Sparkles className="mr-2 h-4 w-4" /> Generate Reasoning
          </Button>
          <Label className="flex items-center gap-2 cursor-pointer">
            <Upload className="h-4 w-4" /> Upload TXT
            <Input type="file" accept=".txt" className="hidden" onChange={handleTxtUpload} />
          </Label>
          <Label className="flex items-center gap-2 cursor-pointer">
            <Upload className="h-4 w-4" /> Upload KG
            <Input type="file" accept=".json" className="hidden" onChange={handleKgUpload} />
          </Label>
          <Button onClick={() => {
            if (result?.reasoning?.knowledge_graph) {
              const blob = new Blob([JSON.stringify(result.reasoning.knowledge_graph, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'knowledge_graph.json';
              a.click();
              URL.revokeObjectURL(url);
            }
          }} disabled={!result?.reasoning?.knowledge_graph}>
            Download KG
          </Button>
        </div>
      </Card>

      <Tabs value={tab} onValueChange={setTab} className="w-full">
        <TabsList>
          <TabsTrigger value="reasoning">Reasoning</TabsTrigger>
          <TabsTrigger value="validation">Validation</TabsTrigger>
          <TabsTrigger value="graph">Reasoning Pathway</TabsTrigger>
          <TabsTrigger value="kg_explorer">KG Explorer</TabsTrigger>
        </TabsList>

        <TabsContent value="reasoning">
          <Card><CardContent className="p-4 whitespace-pre-wrap text-sm">{JSON.stringify(result?.reasoning, null, 2)}</CardContent></Card>
        </TabsContent>

        <TabsContent value="validation">
          <Card><CardContent className="p-4 whitespace-pre-wrap text-sm">{JSON.stringify(result?.validation, null, 2)}</CardContent></Card>
        </TabsContent>

        <TabsContent value="graph" style={{ height: '500px' }}>
          <ReactFlow nodes={nodes} edges={edges}>
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </TabsContent>

        <TabsContent value="kg_explorer">
          <Card><CardContent className="p-4"><i>Knowledge Graph Explorer coming soon...</i></CardContent></Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
