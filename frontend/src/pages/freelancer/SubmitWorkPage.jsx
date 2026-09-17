// src/pages/freelancer/SubmitWorkPage.jsx
import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import API from '../../api/axios.js'
import FreelancerSidebar from '../../components/FreelancerSidebar.jsx'
import '../../css/Dashboard.css'
import '../../css/Jobs.css'

export default function SubmitWorkPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [project, setProject] = useState(null)
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [formData, setFormData] = useState({
        github_link: '',
        website_url: '',
        file_link: '',
        notes: '',
    })

    useEffect(() => {
        fetchProject()
    }, [id])

    async function fetchProject() {
        try {
            const res = await API.get(`/projects/${id}/`)
            setProject(res.data)
        } catch {
            toast.error('Failed to load project.')
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!formData.github_link && !formData.website_url &&
            !formData.file_link && !formData.notes) {
            toast.error('Please fill in at least one submission field.')
            return
        }

        setSubmitting(true)
        try {
            await API.post(`/projects/${id}/submit-work/`, formData)
            toast.success('Work submitted successfully!')

            navigate('/freelancer/projects')
        } catch (err){
            toast.error(err.response?.data?.error || err?.message || 'Failed to submit work.')
        } finally {
            setSubmitting(false)
        }
    }

    if (loading) return (
        <div className="dashboard-layout">
            <FreelancerSidebar />
            <main className="dashboard-main">
                <div className="spinner"></div>
            </main>
        </div>
    )

    return (
        <div className="dashboard-layout">
            <FreelancerSidebar />

            <main className="dashboard-main">
                <Link
                    to="/freelancer/projects"
                    style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        color: '#f5576c',
                        fontWeight: 600,
                        fontSize: '0.9rem',
                        marginBottom: '24px',
                        textDecoration: 'none',
                    }}
                >
                    {'<-'} Back to Projects
                </Link>

                <div className="dashboard-header">
                    <h1>{project?.work_status === 'revision_requested' ? 'Resubmit Work' : 'Submit Work'}</h1>
                    <p>Submit your work for the client to review and release payment.</p>
                </div>

                <div className="dashboard-card" style={{
                    background: 'linear-gradient(135deg, #f093fb22, #f5576c11)',
                    border: '2px solid #f5576c33',
                }}>
                    <h2 style={{
                        fontSize: '1.15rem',
                        fontWeight: 700,
                        marginBottom: '8px',
                    }}>
                        {project?.job_details?.title}
                    </h2>
                    <p style={{ color: '#888', fontSize: '0.88rem' }}>
                        Client: <strong>{project?.client_details?.username}</strong>
                        {' • '}
                        Earning: <strong style={{ color: '#f5576c' }}>${project?.escrow_amount}</strong>
                    </p>
                </div>

                {project?.revision_notes && (
                    <div style={{
                        background: '#fff3e0',
                        border: '2px solid #ffb74d',
                        borderRadius: '14px',
                        padding: '20px 24px',
                        marginBottom: '24px',
                    }}>
                        <div style={{
                            fontWeight: 700,
                            color: '#e65100',
                            marginBottom: '8px',
                        }}>
                            Client Revision Notes:
                        </div>
                        <p style={{ color: '#555', lineHeight: 1.7 }}>
                            {project.revision_notes}
                        </p>
                    </div>
                )}

                <div className="job-form-card">
                    <p style={{
                        color: '#888',
                        fontSize: '0.9rem',
                        marginBottom: '24px',
                    }}>
                        Fill in at least one field below to submit your work.
                    </p>

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label>GitHub Repository URL</label>
                            <input
                                type="url"
                                name="github_link"
                                placeholder="https://github.com/username/repo"
                                value={formData.github_link}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>Live Website URL</label>
                            <input
                                type="url"
                                name="website_url"
                                placeholder="https://yourproject.com"
                                value={formData.website_url}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>File / Document Link</label>
                            <input
                                type="url"
                                name="file_link"
                                placeholder="https://drive.google.com/..."
                                value={formData.file_link}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-group">
                            <label>Notes to Client</label>
                            <textarea
                                name="notes"
                                placeholder="Describe what you've done, any instructions, or anything the client should know..."
                                value={formData.notes}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-submit-row">
                            <Link to="/freelancer/projects" className="btn-cancel">
                                Cancel
                            </Link>
                            <button
                                type="submit"
                                className="btn-submit-job"
                                style={{ background: 'linear-gradient(135deg, #f093fb, #f5576c)' }}
                                disabled={submitting}
                            >
                                {submitting ? 'Submitting...' : 'Submit Work'}
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    )
}
