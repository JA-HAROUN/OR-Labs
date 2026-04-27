import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SimplexInput } from './simplex-input';

describe('SimplexInput', () => {
  let component: SimplexInput;
  let fixture: ComponentFixture<SimplexInput>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimplexInput]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SimplexInput);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
