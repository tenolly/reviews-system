const ratingDefinitions = [
  { key: 'overall', label: 'Общее впечатление' },
  { key: 'difficulty', label: 'Сложность' },
  { key: 'engagement', label: 'Интерес' },
  { key: 'organization', label: 'Организованность' },
  { key: 'fairness', label: 'Справедливость' }
]

const baseRatings = {
  overall: 5,
  difficulty: 3,
  engagement: 5,
  organization: 4,
  fairness: 5
}

const buildBreakdownFromRatings = (ratings = baseRatings) =>
  ratingDefinitions.map((metric) => ({
    key: metric.key,
    label: metric.label,
    value: ratings[metric.key] ?? 3
  }))

const calculateScore = (ratings = baseRatings) => {
  const values = ratingDefinitions.map((metric) => ratings[metric.key] ?? 3)
  const average = values.reduce((acc, value) => acc + value, 0) / values.length
  return Number(average.toFixed(1))
}

export const getUserReviewMock = () => {
  const ratings = { ...baseRatings }
  return {
    teacherId: 't-1',
    studyYear: '2024/2025',
    subject: 'Проектирование информационных систем',
    tags: ['инновации', 'поддержка', 'практика'],
    comment:
      'Лекции структурированные, требования прозрачные. Достаточно сложно, но очень полезно для портфолио.',
    date: '2025-05-12',
    photo: 'https://i.pravatar.cc/96?img=68',
    ratings,
    breakdown: buildBreakdownFromRatings(ratings),
    score: calculateScore(ratings)
  }
}

export const getUserReviewRatingsDefinition = () => ratingDefinitions.map((definition) => ({ ...definition }))
