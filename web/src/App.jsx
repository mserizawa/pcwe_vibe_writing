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

  const SITE_NAME = 'Vibe Writing Presented by 読んでみてはラジオ'

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

  useEffect(() => {
    const descEl = document.querySelector('meta[name="description"]')
    if (story) {
      document.title = `${story.title} | ${SITE_NAME}`
      if (descEl) descEl.setAttribute('content', story.story.slice(0, 200))
    } else {
      document.title = SITE_NAME
      if (descEl) descEl.setAttribute('content', 'AIが生成したショートショートをお届けします。')
    }
  }, [story])

  return (
    <div
      className="min-h-screen p-2 sm:p-12"
      style={{ backgroundImage: `url(${base}assets/border.png)`, backgroundRepeat: 'repeat', backgroundSize: '100% auto' }}
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

            <a
              href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(`「${story.title}」を読みました！\n#読んでみてはラジオ #PCWE2026 #PCEX2026\n${window.location.href}`)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-10 flex items-center justify-center gap-2 w-full rounded-full bg-black text-white text-sm font-medium py-2.5 hover:bg-gray-800 transition-colors"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true" className="w-4 h-4 fill-current">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.259 5.629L18.244 2.25zM17.083 19.77h1.833L7.084 4.126H5.117L17.083 19.77z" />
              </svg>
              シェアする
            </a>

          </>
        ) : null}
      </div>
      <p className="text-center text-white text-xs py-6">© 2026 <a href="https://yondemiteha.com" target="_blank" rel="noopener noreferrer" className="no-underline">読んでみてはラジオ</a></p>
    </div>
  )
}
