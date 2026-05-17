// frontend/src/components/Annotation/AnnotationTool.tsx
import React, { useState, useRef, useEffect } from 'react'
import { fabric } from 'fabric'

interface AnnotationToolProps {
  imageUrl: string
  onSave: (annotations: any[]) => void
  existingAnnotations?: any[]
}

export const AnnotationTool: React.FC<AnnotationToolProps> = ({
  imageUrl,
  onSave,
  existingAnnotations = []
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvas, setCanvas] = useState<fabric.Canvas | null>(null)
  const [currentTool, setCurrentTool] = useState<'rect' | 'polygon' | 'brush'>('rect')
  const [selectedClass, setSelectedClass] = useState('defect')
  const [annotations, setAnnotations] = useState<any[]>(existingAnnotations)

  // Инициализация Canvas
  useEffect(() => {
    if (!canvasRef.current) return

    const fabricCanvas = new fabric.Canvas(canvasRef.current, {
      width: 800,
      height: 600,
      selection: true,
    })

    // Загрузка изображения
    fabric.Image.fromURL(imageUrl, (img) => {
      const scale = Math.min(
        800 / img.width!,
        600 / img.height!
      )
      img.scale(scale)
      fabricCanvas.setBackgroundImage(img, fabricCanvas.renderAll.bind(fabricCanvas))
      fabricCanvas.setDimensions({
        width: img.width! * scale,
        height: img.height! * scale
      })
    })

    setCanvas(fabricCanvas)

    return () => {
      fabricCanvas.dispose()
    }
  }, [imageUrl])

  // Обработка рисования прямоугольника
  const addRectangle = () => {
    if (!canvas) return

    const rect = new fabric.Rect({
      left: 100,
      top: 100,
      width: 100,
      height: 100,
      fill: 'rgba(255, 0, 0, 0.3)',
      stroke: 'red',
      strokeWidth: 2,
      hasControls: true,
      hasBorders: true,
    })

    canvas.add(rect)
    canvas.setActiveObject(rect)
    canvas.renderAll()
  }

  // Сохранение аннотаций
  const saveAnnotations = () => {
    if (!canvas) return

    const objects = canvas.getObjects()
    const newAnnotations = objects
      .filter(obj => obj !== canvas.backgroundImage)
      .map(obj => ({
        id: obj.data?.id || Math.random().toString(),
        type: obj.type,
        left: obj.left,
        top: obj.top,
        width: obj.width,
        height: obj.height,
        scaleX: obj.scaleX,
        scaleY: obj.scaleY,
        fill: obj.fill,
        stroke: obj.stroke,
        class: selectedClass,
      }))

    setAnnotations(newAnnotations)
    onSave(newAnnotations)
  }

  // Очистка всех аннотаций
  const clearAnnotations = () => {
    if (!canvas) return

    const objects = canvas.getObjects()
    objects.forEach(obj => {
      if (obj !== canvas.backgroundImage) {
        canvas.remove(obj)
      }
    })
    canvas.renderAll()
    setAnnotations([])
  }

  return (
    <div className="annotation-tool">
      <div className="toolbar mb-4 flex gap-2">
        <button
          onClick={addRectangle}
          className={`px-3 py-2 rounded ${currentTool === 'rect' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Прямоугольник
        </button>
        <button
          onClick={saveAnnotations}
          className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Сохранить
        </button>
        <button
          onClick={clearAnnotations}
          className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Очистить
        </button>

        <select
          value={selectedClass}
          onChange={(e) => setSelectedClass(e.target.value)}
          className="px-3 py-2 border rounded"
        >
          <option value="defect">Дефект</option>
          <option value="scratch">Царапина</option>
          <option value="dent">Вмятина</option>
          <option value="crack">Трещина</option>
        </select>
      </div>

      <canvas ref={canvasRef} className="border border-gray-300" />

      <div className="mt-4">
        <h3 className="font-semibold mb-2">Аннотации ({annotations.length})</h3>
        <div className="space-y-1">
          {annotations.map((ann, i) => (
            <div key={i} className="text-sm text-gray-600">
              {ann.type} - {ann.class} - [{Math.round(ann.left)}, {Math.round(ann.top)}]
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}