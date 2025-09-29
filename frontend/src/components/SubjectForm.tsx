import React, { useState, useEffect } from 'react'
import {
  Box,
  TextField,
  Button,
  Chip,
  Typography,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'

import { Subject, SubjectCreate, SubjectUpdate } from '../types/api'
import { useAPI } from '../contexts/APIContext'

interface SubjectFormProps {
  subject?: Subject | null
  onSubmit: (data: SubjectCreate | SubjectUpdate) => void
  isLoading?: boolean
}

export default function SubjectForm({ subject, onSubmit, isLoading = false }: SubjectFormProps) {
  const { subjects } = useAPI()
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    aliases: [] as string[],
    tags: [] as string[],
  })
  const [newAlias, setNewAlias] = useState('')
  const [newTag, setNewTag] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (subject) {
      setFormData({
        name: subject.name,
        description: subject.description || '',
        aliases: subject.aliases,
        tags: subject.tags,
      })
    }
  }, [subject])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (formData.description && formData.description.length > 1000) {
      newErrors.description = 'Description cannot exceed 1000 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    const submitData = {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      aliases: formData.aliases,
      tags: formData.tags,
    }

    if (subject) {
      // Update existing subject
      subjects.update.mutate(
        { id: subject.id, data: submitData },
        {
          onError: (error) => {
            setErrors({ submit: error.message })
          },
        }
      )
    } else {
      // Create new subject
      onSubmit(submitData)
    }
  }

  const addAlias = () => {
    if (newAlias.trim() && !formData.aliases.includes(newAlias.trim())) {
      setFormData(prev => ({
        ...prev,
        aliases: [...prev.aliases, newAlias.trim()]
      }))
      setNewAlias('')
    }
  }

  const removeAlias = (alias: string) => {
    setFormData(prev => ({
      ...prev,
      aliases: prev.aliases.filter(a => a !== alias)
    }))
  }

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }))
      setNewTag('')
    }
  }

  const removeTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }))
  }

  const handleKeyPress = (e: React.KeyboardEvent, action: 'alias' | 'tag') => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (action === 'alias') {
        addAlias()
      } else {
        addTag()
      }
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ pt: 1 }}>
      <TextField
        fullWidth
        label="Name"
        value={formData.name}
        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
        error={!!errors.name}
        helperText={errors.name}
        margin="normal"
        required
      />

      <TextField
        fullWidth
        label="Description"
        value={formData.description}
        onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
        error={!!errors.description}
        helperText={errors.description || `${formData.description.length}/1000 characters`}
        margin="normal"
        multiline
        rows={3}
      />

      <Box mt={2}>
        <Typography variant="subtitle2" gutterBottom>
          Aliases
        </Typography>
        <TextField
          fullWidth
          size="small"
          placeholder="Add alias"
          value={newAlias}
          onChange={(e) => setNewAlias(e.target.value)}
          onKeyPress={(e) => handleKeyPress(e, 'alias')}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={addAlias} size="small">
                  <AddIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <Box mt={1}>
          {formData.aliases.map((alias, index) => (
            <Chip
              key={index}
              label={alias}
              onDelete={() => removeAlias(alias)}
              size="small"
              variant="outlined"
              sx={{ mr: 0.5, mb: 0.5 }}
            />
          ))}
        </Box>
      </Box>

      <Box mt={2}>
        <Typography variant="subtitle2" gutterBottom>
          Tags
        </Typography>
        <TextField
          fullWidth
          size="small"
          placeholder="Add tag"
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          onKeyPress={(e) => handleKeyPress(e, 'tag')}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={addTag} size="small">
                  <AddIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <Box mt={1}>
          {formData.tags.map((tag, index) => (
            <Chip
              key={index}
              label={tag}
              onDelete={() => removeTag(tag)}
              size="small"
              color="primary"
              sx={{ mr: 0.5, mb: 0.5 }}
            />
          ))}
        </Box>
      </Box>

      {errors.submit && (
        <Typography color="error" variant="body2" sx={{ mt: 2 }}>
          {errors.submit}
        </Typography>
      )}

      <Box mt={3} display="flex" justifyContent="flex-end" gap={2}>
        <Button type="submit" variant="contained" disabled={isLoading}>
          {subject ? 'Update' : 'Create'} Subject
        </Button>
      </Box>
    </Box>
  )
}
