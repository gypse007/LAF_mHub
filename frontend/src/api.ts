const API_BASE = 'http://localhost:8000';

export async function uploadWall(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/api/wall/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!res.ok) throw new Error('Upload failed');
    return res.json();
}

export async function uploadReferenceImage(wallId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/api/wall/${wallId}/reference`, {
        method: 'POST',
        body: formData,
    });

    if (!res.ok) throw new Error('Reference upload failed');
    return res.json();
}

export async function updateWallTags(wallId: string, tags: Record<string, string>) {
    const res = await fetch(`${API_BASE}/api/wall/${wallId}/tags`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tags),
    });

    if (!res.ok) throw new Error('Tag update failed');
    return res.json();
}

export async function updatePrintArea(wallId: string, printArea: number[][]) {
    const res = await fetch(`${API_BASE}/api/wall/${wallId}/print-area`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ print_area: printArea }),
    });

    if (!res.ok) throw new Error('Print area update failed');
    return res.json();
}

export async function detectWalls(wallId: string) {
    const res = await fetch(`${API_BASE}/api/wall/${wallId}/detect-walls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });

    if (!res.ok) throw new Error('Wall detection failed');
    return res.json();
}

export async function generateDesign(
    wallId: string,
    style: string,
    printArea?: number[][],
    wallSize?: { width: number; height: number } | null
) {
    const res = await fetch(`${API_BASE}/api/wall/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            wall_id: wallId,
            style,
            print_area: printArea,
            wall_size: wallSize
        }),
    });

    if (!res.ok) throw new Error('Generation failed to start');
    return res.json();
}

export async function checkGenerationStatus(taskId: string) {
    const res = await fetch(`${API_BASE}/api/wall/status/${taskId}`);
    if (!res.ok) throw new Error('Failed to check status');
    return res.json();
}

export async function getStyles() {
    const res = await fetch(`${API_BASE}/api/styles`);
    if (!res.ok) throw new Error('Failed to fetch styles');
    return res.json();
}

export async function getStyleSuggestions(tags: string[]) {
    const res = await fetch(`${API_BASE}/api/styles/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tags }),
    });

    if (!res.ok) throw new Error('Failed to fetch suggestions');
    return res.json();
}

export function getImageUrl(path: string) {
    return `${API_BASE}${path}`;
}
