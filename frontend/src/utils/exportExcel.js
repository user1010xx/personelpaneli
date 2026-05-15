import * as XLSX from 'xlsx'
import { formatLocalDate } from './date'

export const exportRowsToExcel = (rows, sheetName, filePrefix) => {
  const worksheet = XLSX.utils.json_to_sheet(rows)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName.slice(0, 31))
  XLSX.writeFile(workbook, `${filePrefix}_${formatLocalDate()}.xlsx`)
}