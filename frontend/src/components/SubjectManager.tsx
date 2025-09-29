import React, { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
} from '@mui/icons-material'

import { useAPI } from '../contexts/APIContext'
import { Subject, SubjectCreate } from '../types/api'
import SubjectForm from './SubjectForm'

export default function SubjectManager() {
  const { subjects } = useAPI()
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [subjectToDelete, setSubjectToDelete] = useState<Subject | null>(null)

  const handleCreateSubject = (data: SubjectCreate) => {
    subjects.create.mutate(data, {
      onSuccess: () => {
        setIsFormOpen(false)
      },
    })
  }

  const handleEditSubject = (subject: Subject) => {
    setEditingSubject(subject)
    setIsFormOpen(true)
  }

  const handleDeleteSubject = (subject: Subject) => {
    setSubjectToDelete(subject)
    setDeleteConfirmOpen(true)
  }

  const confirmDelete = () => {
    if (subjectToDelete) {
      subjects.delete.mutate(subjectToDelete.id, {
        onSuccess: () => {
          setDeleteConfirmOpen(false)
          setSubjectToDelete(null)
        },
      })
    }
  }

  const handleFormClose = () => {
    setIsFormOpen(false)
    setEditingSubject(null)
  }

  if (subjects.list.isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    )
  }

  if (subjects.list.error) {
    return (
      <Alert severity="error">
        Error loading subjects: {subjects.list.error.message}
      </Alert>
    )
  }

  const subjectsList = subjects.list.data?.results || []

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Investigation Subjects
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsFormOpen(true)}
        >
          Add Subject
        </Button>
      </Box>

      {subjectsList.length === 0 ? (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <PersonIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No subjects yet
              </Typography>
              <Typography variant="body2" color="textSecondary" mb={3}>
                Create your first investigation subject to get started
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setIsFormOpen(true)}
              >
                Add Subject
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {subjectsList.map((subject) => (
            <Grid item xs={12} md={6} lg={4} key={subject.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {subject.name}
                  </Typography>
                  {subject.description && (
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {subject.description}
                    </Typography>
                  )}
                  {subject.aliases.length > 0 && (
                    <Box mb={1}>
                      <Typography variant="caption" display="block" gutterBottom>
                        Aliases:
                      </Typography>
                      <Box>
                        {subject.aliases.map((alias, index) => (
                          <Chip
                            key={index}
                            label={alias}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                  {subject.tags.length > 0 && (
                    <Box>
                      <Typography variant="caption" display="block" gutterBottom>
                        Tags:
                      </Typography>
                      <Box>
                        {subject.tags.map((tag, index) => (
                          <Chip
                            key={index}
                            label={tag}
                            size="small"
                            color="primary"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <IconButton
                    size="small"
                    onClick={() => handleEditSubject(subject)}
                    aria-label="edit"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteSubject(subject)}
                    aria-label="delete"
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Subject Form Dialog */}
      <Dialog open={isFormOpen} onClose={handleFormClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingSubject ? 'Edit Subject' : 'Create New Subject'}
        </DialogTitle>
        <DialogContent>
          <SubjectForm
            subject={editingSubject}
            onSubmit={handleCreateSubject}
            isLoading={subjects.create.isPending || subjects.update.isPending}
          />
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{subjectToDelete?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={subjects.delete.isPending}
          >
            {subjects.delete.isPending ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
