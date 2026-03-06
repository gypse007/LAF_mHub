import { useState, useCallback } from 'react';
import './index.css';
import Stepper from './components/Stepper';
import UploadStep from './components/UploadStep';
import TagStep from './components/TagStep';
import PrintAreaStep from './components/PrintAreaStep';
import StyleStep from './components/StyleStep';
import GenerateStep from './components/GenerateStep';
import ResultStep from './components/ResultStep';
import { uploadWall, getImageUrl, updateWallTags, updatePrintArea, generateDesign, checkGenerationStatus } from './api';

const STEPS = ['Upload', 'Tag', 'Print Area', 'Style', 'Generate', 'Result'];

interface WallState {
  wallId: string | null;
  file: File | null;
  preview: string | null;
  tags: Record<string, string>;
  printArea: number[][];
  selectedStyle: string;
  analysis: Record<string, unknown> | null;
  generatedImageUrl: string | null;
  originalImageUrl: string | null;
  wallSize: { width: number; height: number } | null;
  panels: string[];
  printResolution: string | null;
}

const initialState: WallState = {
  wallId: null,
  file: null,
  preview: null,
  tags: {},
  printArea: [],
  selectedStyle: '',
  analysis: null,
  generatedImageUrl: null,
  originalImageUrl: null,
  wallSize: null,
  panels: [],
  printResolution: null,
};

export default function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [wall, setWall] = useState<WallState>(initialState);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);

  const completeStep = useCallback((step: number) => {
    setCompletedSteps((prev) => (prev.includes(step) ? prev : [...prev, step]));
  }, []);

  // Step 1: Upload
  const handleUpload = useCallback(async (file: File, preview: string) => {
    setWall((prev) => ({ ...prev, file, preview }));

    try {
      const data = await uploadWall(file);
      setWall((prev) => ({
        ...prev,
        wallId: data.wall_id,
        analysis: data.analysis,
      }));
    } catch {
      // Continue without backend — still show the preview
      setWall((prev) => ({ ...prev, wallId: 'local-' + Date.now() }));
    }

    completeStep(0);
    setCurrentStep(1);
  }, [completeStep]);

  // Step 2: Tags
  const handleTagsChange = useCallback((tags: Record<string, string>) => {
    setWall((prev) => ({ ...prev, tags }));
  }, []);

  const handleTagsNext = useCallback(async () => {
    if (wall.wallId && !wall.wallId.startsWith('local-')) {
      try {
        await updateWallTags(wall.wallId, wall.tags);
      } catch { /* continue */ }
    }
    completeStep(1);
    setCurrentStep(2);
  }, [wall.wallId, wall.tags, completeStep]);

  // Step 3: Print Area
  const handlePrintAreaChange = useCallback((area: number[][]) => {
    setWall((prev) => ({ ...prev, printArea: area }));
  }, []);

  const handlePrintAreaNext = useCallback(async () => {
    if (wall.wallId && !wall.wallId.startsWith('local-') && wall.printArea.length > 0) {
      try {
        await updatePrintArea(wall.wallId, wall.printArea);
      } catch { /* continue */ }
    }
    completeStep(2);
    setCurrentStep(3);
  }, [wall.wallId, wall.printArea, completeStep]);

  // Step 4: Style
  const handleStyleSelect = useCallback((styleId: string) => {
    setWall((prev) => ({ ...prev, selectedStyle: styleId }));
  }, []);

  // Step 5: Generate
  const handleGenerate = useCallback(async (styleOverride?: string) => {
    const style = styleOverride || wall.selectedStyle;
    if (!style) return;

    completeStep(3);
    setCurrentStep(4);
    setIsGenerating(true);
    setGenerateError(null);

    try {
      const startRes = await generateDesign(
        wall.wallId!,
        style,
        wall.printArea.length > 0 ? wall.printArea : undefined,
        wall.wallSize
      );

      const taskId = startRes.task_id;
      if (!taskId) throw new Error("No task ID returned");

      let status = "pending";
      let data = null;

      while (status === "pending" || status === "processing") {
        await new Promise(resolve => setTimeout(resolve, 3000));
        const statusRes = await checkGenerationStatus(taskId);
        status = statusRes.status;

        if (status === "completed") {
          data = statusRes.result;
          break;
        } else if (status === "failed") {
          throw new Error(statusRes.error || 'Generation failed on backend');
        }
      }

      if (!data) throw new Error("No generation data returned");

      setWall((prev) => ({
        ...prev,
        generatedImageUrl: getImageUrl(data.image_url),
        originalImageUrl: getImageUrl(data.original_image_url),
        selectedStyle: style,
        panels: data.panels ? data.panels.map(getImageUrl) : [],
        printResolution: data.print_resolution || null,
      }));
      completeStep(4);
      setCurrentStep(5);
    } catch (err) {
      setGenerateError(err instanceof Error ? err.message : 'Generation failed. Is the backend running?');
    } finally {
      setIsGenerating(false);
    }
  }, [wall.wallId, wall.selectedStyle, wall.printArea, completeStep]);

  // Regenerate with different style
  const handleRegenerate = useCallback((style: string) => {
    handleGenerate(style);
  }, [handleGenerate]);

  // Start over
  const handleStartOver = useCallback(() => {
    setWall(initialState);
    setCurrentStep(0);
    setCompletedSteps([]);
    setGenerateError(null);
    setIsGenerating(false);
  }, []);

  const handleStepClick = useCallback((step: number) => {
    if (completedSteps.includes(step) || step === currentStep) {
      setCurrentStep(step);
    }
  }, [completedSteps, currentStep]);


  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">🎨</div>
          Wall Mural AI
        </div>
        <div className="header-badge">MVP · Powered by AI Agents</div>
      </header>

      <main className="main-content">
        <Stepper
          steps={STEPS}
          currentStep={currentStep}
          onStepClick={handleStepClick}
          completedSteps={completedSteps}
        />

        {/* Step 1: Upload */}
        {currentStep === 0 && (
          <UploadStep
            onUpload={handleUpload}
            preview={wall.preview}
          />
        )}

        {/* Step 2: Tag */}
        {currentStep === 1 && (
          <>
            <TagStep tags={wall.tags} onTagsChange={handleTagsChange} />
            <div className="btn-group">
              <button className="btn btn-secondary" onClick={() => setCurrentStep(0)}>
                ← Back
              </button>
              <button className="btn btn-primary" onClick={handleTagsNext}>
                Continue →
              </button>
            </div>
          </>
        )}

        {/* Step 3: Print Area Setup */}
        {currentStep === 2 && wall.preview && (
          <div className="card fade-in">
            <PrintAreaStep
              wallId={wall.wallId!}
              imagePreview={wall.preview}
              printArea={wall.printArea}
              onPrintAreaChange={handlePrintAreaChange}
              wallSize={wall.wallSize}
              onWallSizeChange={(size) => setWall((prev) => ({ ...prev, wallSize: size }))}
            />
            <div className="btn-group">
              <button className="btn btn-secondary" onClick={() => setCurrentStep(1)}>
                ← Back
              </button>
              <button className="btn btn-primary" onClick={handlePrintAreaNext}>
                {wall.printArea.length > 0 ? 'Continue →' : 'Skip (use default area) →'}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Style */}
        {currentStep === 3 && (
          <>
            <StyleStep
              wallId={wall.wallId!}
              selectedStyle={wall.selectedStyle}
              onStyleSelect={handleStyleSelect}
              wallTags={wall.tags}
            />
            <div className="btn-group">
              <button className="btn btn-secondary" onClick={() => setCurrentStep(2)}>
                ← Back
              </button>
              <button
                className="btn btn-success"
                disabled={!wall.selectedStyle}
                onClick={() => handleGenerate()}
              >
                🚀 Generate Mural
              </button>
            </div>
          </>
        )}

        {/* Step 5: Generating */}
        {currentStep === 4 && (
          <>
            <GenerateStep isLoading={isGenerating} error={generateError} />
            {generateError && (
              <div className="btn-group">
                <button className="btn btn-secondary" onClick={() => setCurrentStep(3)}>
                  ← Back to Style
                </button>
                <button className="btn btn-primary" onClick={() => handleGenerate()}>
                  🔄 Retry
                </button>
              </div>
            )}
          </>
        )}

        {/* Step 6: Result */}
        {currentStep === 5 && wall.generatedImageUrl && wall.originalImageUrl && (
          <ResultStep
            originalImageUrl={wall.originalImageUrl}
            generatedImageUrl={wall.generatedImageUrl}
            panels={wall.panels}
            printResolution={wall.printResolution || undefined}
            onRegenerate={handleRegenerate}
            onStartOver={handleStartOver}
          />
        )}
      </main>
    </div>
  );
}
