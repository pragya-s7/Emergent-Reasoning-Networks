import React, { useState, ChangeEvent } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@radix-ui/react-label";
import { Upload, Sparkles } from "lucide-react";

// Define types
interface ReasoningResult {
  conclusion?: string;
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
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [tab, setTab] = useState<string>("reasoning");
  const [loading, setLoading] = useState<boolean>(false);

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
          openai_key: apiKey,
          run_validation: true
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

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPdfFile(file);
    const formData = new FormData();
    formData.append("file", file);
    try {
      await fetch("/api/ingest", { method: "POST", body: formData });
      alert("PDF ingested successfully.");
    } catch (err) {
      console.error("Ingestion failed:", err);
    }
  };


  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold tracking-tight">Kairos Reasoning Network</h1>
      <Card className="p-4 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="apiKey">OpenAI API Key</Label>
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
            <Upload className="h-4 w-4" /> Upload PDF
            <Input type="file" accept="application/pdf" className="hidden" onChange={handleFileUpload} />
          </Label>
        </div>
      </Card>

      <Tabs value={tab} onValueChange={setTab} className="w-full">
        <TabsList>
          <TabsTrigger value="reasoning">Reasoning</TabsTrigger>
          <TabsTrigger value="validation">Validation</TabsTrigger>
          <TabsTrigger value="graph">Reasoning Pathway</TabsTrigger>
        </TabsList>

        <TabsContent value="reasoning">
          <Card><CardContent className="p-4 whitespace-pre-wrap text-sm">{JSON.stringify(result?.reasoning, null, 2)}</CardContent></Card>
        </TabsContent>

        <TabsContent value="validation">
          <Card><CardContent className="p-4 whitespace-pre-wrap text-sm">{JSON.stringify(result?.validation, null, 2)}</CardContent></Card>
        </TabsContent>

        <TabsContent value="graph">
          <Card><CardContent className="p-4"><i>Reasoning graph visualization coming soon...</i></CardContent></Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
