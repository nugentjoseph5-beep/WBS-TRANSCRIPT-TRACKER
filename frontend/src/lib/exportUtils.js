import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Capture a DOM element as an image
 * @param {HTMLElement} element - The element to capture
 * @param {Object} options - html2canvas options
 * @returns {Promise<string>} - Base64 encoded image
 */
export const captureElementAsImage = async (element, options = {}) => {
  try {
    const canvas = await html2canvas(element, {
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      ...options
    });
    return canvas.toDataURL('image/png');
  } catch (error) {
    console.error('Error capturing element:', error);
    throw error;
  }
};

/**
 * Export analytics dashboard as PDF
 * @param {Object} analytics - Analytics data
 * @param {Object} chartElements - Object containing chart DOM elements
 */
export const exportAnalyticsToPDF = async (analytics, chartElements) => {
  try {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 15;
    let yPosition = margin;

    // Add header
    pdf.setFontSize(20);
    pdf.setTextColor(128, 0, 0); // Maroon
    pdf.text('WBS Transcript & Recommendation Tracker', margin, yPosition);
    yPosition += 10;

    pdf.setFontSize(14);
    pdf.setTextColor(0, 0, 0);
    pdf.text('Analytics Report', margin, yPosition);
    yPosition += 8;

    pdf.setFontSize(10);
    pdf.setTextColor(100, 100, 100);
    pdf.text(`Generated on: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}`, margin, yPosition);
    yPosition += 12;

    // Add summary statistics
    pdf.setFontSize(12);
    pdf.setTextColor(0, 0, 0);
    pdf.text('Summary Statistics', margin, yPosition);
    yPosition += 8;

    const summaryData = [
      ['Metric', 'Transcripts', 'Recommendations'],
      ['Total Requests', analytics.total_requests || 0, analytics.total_recommendation_requests || 0],
      ['Pending', analytics.pending_requests || 0, analytics.pending_recommendation_requests || 0],
      ['In Progress', analytics.in_progress_requests || 0, analytics.in_progress_recommendation_requests || 0],
      ['Completed', analytics.completed_requests || 0, analytics.completed_recommendation_requests || 0],
      ['Rejected', analytics.rejected_requests || 0, analytics.rejected_recommendation_requests || 0],
      ['Overdue', analytics.overdue_requests || 0, analytics.overdue_recommendation_requests || 0],
    ];

    pdf.autoTable({
      startY: yPosition,
      head: [summaryData[0]],
      body: summaryData.slice(1),
      theme: 'grid',
      headStyles: { fillColor: [128, 0, 0] },
      margin: { left: margin, right: margin },
    });

    yPosition = pdf.lastAutoTable.finalY + 15;

    // Add charts
    const charts = Object.entries(chartElements);
    for (let i = 0; i < charts.length; i++) {
      const [chartName, chartElement] = charts[i];
      
      if (!chartElement) continue;

      // Check if we need a new page
      if (yPosition + 80 > pageHeight - margin) {
        pdf.addPage();
        yPosition = margin;
      }

      // Add chart title
      pdf.setFontSize(11);
      pdf.setTextColor(0, 0, 0);
      pdf.text(chartName, margin, yPosition);
      yPosition += 5;

      try {
        const chartImage = await captureElementAsImage(chartElement);
        const imgWidth = pageWidth - (2 * margin);
        const imgHeight = 70;

        pdf.addImage(chartImage, 'PNG', margin, yPosition, imgWidth, imgHeight);
        yPosition += imgHeight + 10;
      } catch (error) {
        console.error(`Error capturing chart ${chartName}:`, error);
        pdf.setFontSize(9);
        pdf.setTextColor(255, 0, 0);
        pdf.text('Error capturing chart', margin, yPosition);
        yPosition += 10;
      }
    }

    // Save the PDF
    pdf.save(`analytics-report-${new Date().toISOString().split('T')[0]}.pdf`);
    return true;
  } catch (error) {
    console.error('Error generating PDF:', error);
    throw error;
  }
};

/**
 * Export analytics to CSV format
 * @param {Object} analytics - Analytics data
 */
export const exportAnalyticsToCSV = (analytics) => {
  const csvData = [
    ['Metric', 'Transcripts', 'Recommendations'],
    ['Total Requests', analytics.total_requests || 0, analytics.total_recommendation_requests || 0],
    ['Pending', analytics.pending_requests || 0, analytics.pending_recommendation_requests || 0],
    ['In Progress', analytics.in_progress_requests || 0, analytics.in_progress_recommendation_requests || 0],
    ['Processing', analytics.processing_requests || 0, 0],
    ['Ready', analytics.ready_requests || 0, 0],
    ['Completed', analytics.completed_requests || 0, analytics.completed_recommendation_requests || 0],
    ['Rejected', analytics.rejected_requests || 0, analytics.rejected_recommendation_requests || 0],
    ['Overdue', analytics.overdue_requests || 0, analytics.overdue_recommendation_requests || 0],
  ];

  const csvContent = csvData.map(row => row.join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `analytics-data-${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
