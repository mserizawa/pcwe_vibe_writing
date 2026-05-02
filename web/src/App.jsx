import { useState, useEffect } from 'react'

function getUuid() {
  return window.location.hash.slice(1)
}

export default function App() {
  const [uuid, setUuid] = useState(getUuid)
  const [story, setStory] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const onHashChange = () => setUuid(getUuid())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  useEffect(() => {
    setStory(null)
    setError(null)

    if (!uuid) {
      setError('URLにIDが指定されていません')
      return
    }

    fetch(`/shorts/${uuid}.json`)
      .then((res) => {
        if (!res.ok) throw new Error()
        return res.json()
      })
      .then(setStory)
      .catch(() => setError('小説が見つかりませんでした'))
  }, [uuid])

  return (
    <div
      className="min-h-screen p-2 sm:p-12"
      style={{ backgroundImage: 'url(/assets/border.png)', backgroundRepeat: 'repeat' }}
    >
      <div className="bg-white rounded-3xl w-full max-w-sm mx-auto px-8 py-10 min-h-[calc(100vh-1rem)] sm:min-h-0">
        {error ? (
          <p className="text-gray-400 text-sm text-center mt-8">{error}</p>
        ) : story ? (
          <>
            <h1 className="text-xl font-bold text-gray-900 mb-6 leading-snug">{story.title}</h1>
            <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{story.story}</p>
            <p className="text-xs text-gray-400 mt-6">
              生成日: {new Date(story.created_at).toLocaleDateString('ja-JP')}
            </p>
            <div className="flex justify-center py-8">
              <img src="/assets/logo.jpg" alt="logo" className="w-1/4" />
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}
