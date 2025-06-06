from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from io import BytesIO
import plotly.io as pio
import base64
import os
from datetime import datetime
from typing import List, Dict, Any

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12
        ))
    
    def _create_pie_chart(self, data: Dict[str, float], title: str) -> Drawing:
        """Create a pie chart using ReportLab."""
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 0
        pie.width = 200
        pie.height = 200
        pie.data = list(data.values())
        pie.labels = list(data.keys())
        pie.slices.strokeWidth = 0.5
        
        # Add title
        title_label = Label()
        title_label.setText(title)
        title_label.x = 200
        title_label.y = 190
        title_label.fontSize = 14
        title_label.textAnchor = 'middle'
        drawing.add(title_label)
        
        drawing.add(pie)
        return drawing
    
    def _create_line_chart(self, data: List[float], title: str) -> Drawing:
        """Create a line chart using ReportLab."""
        drawing = Drawing(400, 200)
        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        chart.data = [data]
        chart.categoryAxis.categoryNames = [str(i+1) for i in range(len(data))]
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 1
        chart.valueAxis.valueStep = 0.2
        
        # Add title
        title_label = Label()
        title_label.setText(title)
        title_label.x = 200
        title_label.y = 190
        title_label.fontSize = 14
        title_label.textAnchor = 'middle'
        drawing.add(title_label)
        
        drawing.add(chart)
        return drawing
    
    def _plotly_to_image(self, fig) -> bytes:
        """Convert Plotly figure to image bytes."""
        img_bytes = pio.to_image(fig, format='png')
        return img_bytes
    
    def generate_report(self, interview_data: Dict[str, Any], output_path: str) -> str:
        """
        Generate a PDF report for the interview session.
        
        Args:
            interview_data: Dictionary containing interview results and analytics
            output_path: Path to save the PDF report
            
        Returns:
            str: Path to the generated PDF file
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Container for PDF elements
        elements = []
        
        # Title
        elements.append(Paragraph(
            "Interview Performance Report",
            self.styles['CustomTitle']
        ))
        
        # Date and Time
        elements.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 20))
        
        # Summary Section
        elements.append(Paragraph("Summary", self.styles['CustomHeading']))
        summary_data = [
            ["Total Questions", str(interview_data['total_questions'])],
            ["Correct Answers", str(interview_data['correct_answers'])],
            ["Accuracy", f"{interview_data['accuracy']:.1f}%"],
            ["Average Score", f"{interview_data['average_score']:.1f}%"]
        ]
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Answer Distribution Chart
        elements.append(Paragraph("Answer Distribution", self.styles['CustomHeading']))
        answer_dist = {
            "Correct": interview_data['correct_answers'],
            "Incorrect": interview_data['total_questions'] - interview_data['correct_answers']
        }
        elements.append(self._create_pie_chart(answer_dist, "Answer Distribution"))
        elements.append(Spacer(1, 20))
        
        # Question Categories Chart
        elements.append(Paragraph("Question Categories", self.styles['CustomHeading']))
        elements.append(self._create_pie_chart(interview_data['categories'], "Question Categories"))
        elements.append(Spacer(1, 20))
        
        # Performance Over Time
        elements.append(Paragraph("Performance Over Time", self.styles['CustomHeading']))
        elements.append(self._create_line_chart(interview_data['scores'], "Similarity Scores"))
        elements.append(Spacer(1, 20))
        
        # Category-wise Performance
        elements.append(Paragraph("Category-wise Performance", self.styles['CustomHeading']))
        category_data = [["Category", "Average Score", "Status"]]
        for category, score in interview_data['category_scores'].items():
            if score:  # Only include categories with questions
                avg_score = sum(score) / len(score)
                status = "Good" if avg_score >= 0.5 else "Needs Improvement"
                category_data.append([
                    category,
                    f"{avg_score:.1%}",
                    status
                ])
        
        category_table = Table(category_data, colWidths=[2*inch, 2*inch, 2*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(category_table)
        elements.append(Spacer(1, 20))
        
        # Recommendations
        elements.append(Paragraph("Recommendations", self.styles['CustomHeading']))
        recommendations = self._generate_recommendations(interview_data)
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(elements)
        return output_path
    
    def _generate_recommendations(self, interview_data: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on interview performance."""
        recommendations = []
        
        # Overall performance recommendations
        if interview_data['accuracy'] < 50:
            recommendations.append(
                "Focus on improving your overall understanding of core concepts. "
                "Consider reviewing fundamental topics in your field."
            )
        elif interview_data['accuracy'] < 75:
            recommendations.append(
                "Your performance is good, but there's room for improvement. "
                "Focus on areas where you scored below average."
            )
        else:
            recommendations.append(
                "Excellent performance! Continue practicing to maintain your high standards "
                "and focus on advanced topics."
            )
        
        # Category-specific recommendations
        for category, scores in interview_data['category_scores'].items():
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score < 0.5:
                    recommendations.append(
                        f"Your {category} skills need improvement. "
                        f"Consider practicing more {category.lower()} questions and reviewing related concepts."
                    )
                elif avg_score < 0.7:
                    recommendations.append(
                        f"Your {category} performance is decent but could be better. "
                        f"Focus on understanding the underlying principles better."
                    )
        
        # Follow-up recommendations
        if interview_data.get('total_follow_ups', 0) > 0:
            if interview_data.get('avg_follow_up_score', 0) < 0.5:
                recommendations.append(
                    "You need to improve your ability to handle follow-up questions. "
                    "Practice thinking on your feet and providing detailed explanations."
                )
        
        return recommendations 