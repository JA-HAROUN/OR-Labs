import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-simplex-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './simplex-results.html',
  styleUrl: './simplex-results.css',
})
export class SimplexResults {
  @Input() responseData: any = null;
}
