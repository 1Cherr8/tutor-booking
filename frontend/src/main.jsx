import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const API = '/api'

async function api(path, options = {}) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(`${API}${path}`, { ...options, headers })
  if (response.status === 204) return null

  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.detail || 'Ошибка запроса')
  return data
}

function Auth({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      const data = await api(`/auth/${mode}`, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      localStorage.setItem('token', data.access_token)
      onLogin(data.user)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="auth-wrap">
      <form className="card auth-card" onSubmit={submit}>
        <h1>Tutor Booking</h1>
        <p>{mode === 'login' ? 'Вход в систему' : 'Регистрация клиента'}</p>
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" type="email" required />
        <input value={password} onChange={e => setPassword(e.target.value)} placeholder="Пароль" type="password" minLength="6" required />
        {error && <div className="error">{error}</div>}
        <button type="submit">{mode === 'login' ? 'Войти' : 'Зарегистрироваться'}</button>
        <button type="button" className="secondary" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? 'Создать аккаунт' : 'У меня уже есть аккаунт'}
        </button>
      </form>
    </div>
  )
}

function SubjectForm({ initial, onSave, onCancel }) {
  const [form, setForm] = useState(initial || {
    title: '', description: '', price: 1200, duration_minutes: 60, is_active: true,
  })

  function change(name, value) {
    setForm({ ...form, [name]: value })
  }

  return (
    <form className="card form-grid" onSubmit={e => { e.preventDefault(); onSave(form) }}>
      <h3>{initial ? 'Редактировать предмет' : 'Новый предмет'}</h3>
      <input value={form.title} onChange={e => change('title', e.target.value)} placeholder="Название" required />
      <textarea value={form.description} onChange={e => change('description', e.target.value)} placeholder="Описание" />
      <input value={form.price} onChange={e => change('price', Number(e.target.value))} type="number" min="0" placeholder="Цена" required />
      <input value={form.duration_minutes} onChange={e => change('duration_minutes', Number(e.target.value))} type="number" min="15" placeholder="Длительность, мин" required />
      <label><input type="checkbox" checked={form.is_active} onChange={e => change('is_active', e.target.checked)} /> Доступен для записи</label>
      <div className="actions"><button>Сохранить</button>{onCancel && <button type="button" className="secondary" onClick={onCancel}>Отмена</button>}</div>
    </form>
  )
}

function BookingForm({ subjects, initial, onSave, onCancel, isAdmin }) {
  const [form, setForm] = useState(initial || {
    subject_id: subjects[0]?.id || '',
    start_time: '',
    status: 'planned',
    comment: '',
  })

  function toInputDate(value) {
    if (!value) return ''
    return value.slice(0, 16)
  }

  return (
    <form className="card form-grid" onSubmit={e => {
      e.preventDefault()
      onSave({ ...form, subject_id: Number(form.subject_id), start_time: form.start_time.length === 16 ? `${form.start_time}:00` : form.start_time })
    }}>
      <h3>{initial ? 'Редактировать запись' : 'Новая запись'}</h3>
      <select value={form.subject_id} onChange={e => setForm({ ...form, subject_id: e.target.value })} required>
        <option value="">Выберите предмет</option>
        {subjects.filter(s => s.is_active || initial?.subject_id === s.id).map(s => <option key={s.id} value={s.id}>{s.title}</option>)}
      </select>
      <input type="datetime-local" value={toInputDate(form.start_time)} onChange={e => setForm({ ...form, start_time: e.target.value })} required />
      <textarea value={form.comment} onChange={e => setForm({ ...form, comment: e.target.value })} placeholder="Комментарий" />
      {initial && isAdmin && <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
        <option value="planned">planned</option>
        <option value="completed">completed</option>
        <option value="cancelled">cancelled</option>
      </select>}
      <div className="actions"><button>Сохранить</button>{onCancel && <button type="button" className="secondary" onClick={onCancel}>Отмена</button>}</div>
    </form>
  )
}

function App() {
  const [user, setUser] = useState(null)
  const [subjects, setSubjects] = useState([])
  const [bookings, setBookings] = useState([])
  const [message, setMessage] = useState('')
  const [subjectEdit, setSubjectEdit] = useState(null)
  const [showSubjectForm, setShowSubjectForm] = useState(false)
  const [bookingEdit, setBookingEdit] = useState(null)
  const [showBookingForm, setShowBookingForm] = useState(false)

  useEffect(() => {
    if (!localStorage.getItem('token')) return
    api('/auth/me').then(setUser).catch(() => localStorage.removeItem('token'))
  }, [])

  useEffect(() => {
    if (user) refresh()
  }, [user])

  async function refresh() {
    try {
      const [s, b] = await Promise.all([api('/subjects'), api('/bookings')])
      setSubjects(s)
      setBookings(b)
    } catch (err) {
      setMessage(err.message)
    }
  }

  function logout() {
    localStorage.removeItem('token')
    setUser(null)
  }

  async function saveSubject(form) {
    try {
      if (subjectEdit) {
        await api(`/subjects/${subjectEdit.id}`, { method: 'PUT', body: JSON.stringify(form) })
      } else {
        await api('/subjects', { method: 'POST', body: JSON.stringify(form) })
      }
      setSubjectEdit(null); setShowSubjectForm(false); await refresh()
    } catch (err) { setMessage(err.message) }
  }

  async function deleteSubject(id) {
    if (!confirm('Удалить предмет?')) return
    try { await api(`/subjects/${id}`, { method: 'DELETE' }); await refresh() }
    catch (err) { setMessage(err.message) }
  }

  async function saveBooking(form) {
    try {
      if (bookingEdit) {
        await api(`/bookings/${bookingEdit.id}`, { method: 'PUT', body: JSON.stringify(form) })
      } else {
        await api('/bookings', { method: 'POST', body: JSON.stringify(form) })
      }
      setBookingEdit(null); setShowBookingForm(false); await refresh()
    } catch (err) { setMessage(err.message) }
  }

  async function deleteBooking(id) {
    if (!confirm('Удалить запись?')) return
    try { await api(`/bookings/${id}`, { method: 'DELETE' }); await refresh() }
    catch (err) { setMessage(err.message) }
  }

  if (!user) return <Auth onLogin={setUser} />

  return (
    <div className="container">
      <header>
        <div><h1>Tutor Booking</h1><span>{user.email} · {user.role}</span></div>
        <button className="secondary" onClick={logout}>Выйти</button>
      </header>

      {message && <div className="error" onClick={() => setMessage('')}>{message}</div>}

      <section>
        <div className="section-title"><h2>Предметы</h2>{user.role === 'admin' && <button onClick={() => { setSubjectEdit(null); setShowSubjectForm(true) }}>Добавить</button>}</div>
        {showSubjectForm && <SubjectForm initial={subjectEdit} onSave={saveSubject} onCancel={() => { setShowSubjectForm(false); setSubjectEdit(null) }} />}
        <div className="grid">
          {subjects.map(s => <div className="card" key={s.id}>
            <h3>{s.title}</h3><p>{s.description}</p><p><b>{s.price} ₽</b> · {s.duration_minutes} мин</p>
            <small>{s.is_active ? 'Доступен' : 'Отключён'}</small>
            {user.role === 'admin' && <div className="actions">
              <button onClick={() => { setSubjectEdit(s); setShowSubjectForm(true) }}>Изменить</button>
              <button className="danger" onClick={() => deleteSubject(s.id)}>Удалить</button>
            </div>}
          </div>)}
        </div>
      </section>

      <section>
        <div className="section-title"><h2>{user.role === 'admin' ? 'Все записи' : 'Мои записи'}</h2>{user.role !== 'admin' && <button onClick={() => { setBookingEdit(null); setShowBookingForm(true) }}>Новая запись</button>}</div>
        {showBookingForm && <BookingForm subjects={subjects} initial={bookingEdit} onSave={saveBooking} isAdmin={user.role === 'admin'} onCancel={() => { setShowBookingForm(false); setBookingEdit(null) }} />}
        <div className="table-wrap">
          <table>
            <thead><tr>{user.role === 'admin' && <th>Клиент</th>}<th>Предмет</th><th>Дата</th><th>Статус</th><th>Комментарий</th><th></th></tr></thead>
            <tbody>
              {bookings.map(b => <tr key={b.id}>
                {user.role === 'admin' && <td>{b.client_email}</td>}
                <td>{b.subject_title}</td>
                <td>{new Date(b.start_time).toLocaleString()}</td>
                <td>{b.status}</td>
                <td>{b.comment}</td>
                <td className="actions">
                  <button onClick={() => { setBookingEdit(b); setShowBookingForm(true) }}>Изменить</button>
                  <button className="danger" onClick={() => deleteBooking(b.id)}>Удалить</button>
                </td>
              </tr>)}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
