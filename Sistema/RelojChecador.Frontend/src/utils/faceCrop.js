function getDetectionBox(detection) {
  const box = detection.box || detection.detection?.box;

  if (!box) {
    throw new Error("No se encontró el cuadro del rostro detectado.");
  }

  return box;
}

export function expandFaceBox(box, sourceWidth, sourceHeight) {
  const extraTop = box.height * 0.5;
  const extraBottom = box.height * 0.14;
  const extraSide = box.width * 0.2;

  const x = Math.max(0, Math.floor(box.x - extraSide));
  const y = Math.max(0, Math.floor(box.y - extraTop));
  const width = Math.min(sourceWidth - x, Math.ceil(box.width + extraSide * 2));
  const height = Math.min(sourceHeight - y, Math.ceil(box.height + extraTop + extraBottom));

  return { x, y, width, height };
}

export function cropFaceToDataUrl(video, detection, options = {}) {
  const {
    outputWidth = null,
    outputHeight = null,
    quality = 0.92,
  } = options;

  const box = getDetectionBox(detection);
  const sourceWidth = video.videoWidth;
  const sourceHeight = video.videoHeight;
  const expandedBox = expandFaceBox(box, sourceWidth, sourceHeight);

  if (expandedBox.width <= 0 || expandedBox.height <= 0) {
    throw new Error("El recorte del rostro no tiene dimensiones válidas.");
  }

  const canvas = document.createElement("canvas");
  canvas.width = outputWidth || expandedBox.width;
  canvas.height = outputHeight || expandedBox.height;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(
    video,
    expandedBox.x,
    expandedBox.y,
    expandedBox.width,
    expandedBox.height,
    0,
    0,
    canvas.width,
    canvas.height
  );

  return canvas.toDataURL("image/jpeg", quality);
}

export function drawExpandedFaceBox(ctx, detection, sourceWidth, sourceHeight) {
  const box = getDetectionBox(detection);
  const expandedBox = expandFaceBox(box, sourceWidth, sourceHeight);
  const score = detection.score ?? detection.detection?.score;

  ctx.save();
  ctx.strokeStyle = "#3ecbff";
  ctx.lineWidth = 3;
  ctx.shadowColor = "rgba(62, 203, 255, 0.85)";
  ctx.shadowBlur = 12;
  ctx.strokeRect(expandedBox.x, expandedBox.y, expandedBox.width, expandedBox.height);

  if (score != null) {
    const label = score.toFixed(2);
    const labelWidth = Math.max(46, label.length * 10 + 10);
    const labelHeight = 20;
    const labelY = Math.max(0, expandedBox.y - labelHeight);

    ctx.fillStyle = "#3ecbff";
    ctx.shadowBlur = 0;
    ctx.fillRect(expandedBox.x, labelY, labelWidth, labelHeight);
    ctx.fillStyle = "#021526";
    ctx.font = "bold 12px Arial";
    ctx.fillText(label, expandedBox.x + 6, labelY + 14);
  }

  ctx.restore();
}
