import {
  ValidationArguments,
  ValidatorConstraint,
  ValidatorConstraintInterface
} from 'class-validator';
import { marketFiltersHierarchyError, MarketFilterSelection } from '../domain/applied-market-filters.domain';

/**
 * Cross-field hierarchy validator applied to a filter property. It inspects the
 * whole DTO object (not the decorated property value) so it can be placed on any
 * filter field that is present when filters are applied.
 */
@ValidatorConstraint({ name: 'marketFilterHierarchy', async: false })
export class MarketFilterHierarchyConstraint implements ValidatorConstraintInterface {
  validate(_value: unknown, args: ValidationArguments): boolean {
    const selection = args.object as MarketFilterSelection;
    return marketFiltersHierarchyError(selection) === null;
  }

  defaultMessage(): string {
    return 'Invalid market filter hierarchy: model requires make; trim requires make and model; year requires make, model, and trim';
  }
}