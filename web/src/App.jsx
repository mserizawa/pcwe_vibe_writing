import { useState, useEffect } from 'react'

const base = import.meta.env.BASE_URL

function getUuid() {
  return window.location.hash.slice(1)
}

function formatCreatedAt(iso) {
  const d = new Date(iso)
  const date = d.toLocaleDateString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit' })
  const time = d.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  return `${date} ${time}`
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

    fetch(`${base}shorts/${uuid}.json`)
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
      style={{ backgroundImage: `url(${base}assets/border.png)`, backgroundRepeat: 'repeat' }}
    >
      <div className="flex justify-center py-6">
        <img src={`${base}assets/vw_logo.png`} alt="Vibe Writing" className="w-2/3 max-w-xs" />
      </div>
      <div className="bg-white rounded-3xl w-full max-w-sm mx-auto px-8 py-10 sm:min-h-0">
        {error ? (
          <p className="text-gray-400 text-sm text-center mt-8">{error}</p>
        ) : story ? (
          <>
            <h1 className="text-xl font-bold text-gray-900 mb-6 leading-snug">{story.title}</h1>
            <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{story.story}</p>

            <hr className="mt-6 border-gray-100" />

            <p className="text-xs text-gray-400 mt-4">
              生成日時: {formatCreatedAt(story.created_at)}
            </p>

            {story.elements && story.elements.length > 0 && (
              <dl className="mt-3 space-y-2">
                {story.elements.map((el) => (
                  <div key={el.category} className="text-xs">
                    <dt className="text-gray-400 mb-1">{el.category}</dt>
                    <dd className="flex flex-wrap gap-1">
                      {el.values.map((v) => <mark key={v}>{v}</mark>)}
                    </dd>
                  </div>
                ))}
              </dl>
            )}

            <div className="flex justify-center py-8">
              <img src={`${base}assets/logo.jpg`} alt="logo" className="w-1/4" />
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}
